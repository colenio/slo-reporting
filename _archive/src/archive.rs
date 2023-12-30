use std::io;
use chrono::{DateTime, TimeZone, Utc};
use csv::{Reader, Writer};
use prometheus_http_query::response::{Sample};


pub struct Archive {
    pub header: Vec<String>,
    pub rows: Vec<Row>,
}

pub struct Row {
    pub time: DateTime<Utc>,
    pub values: Vec<f64>,
}

impl Archive {
    pub fn new(header: Vec<String>) -> Self {
        Self {
            header,
            rows: Vec::new(),
        }
    }

    pub fn read<R: io::Read>(&mut self, mut reader: Reader<R>) -> Reader<R> {
        let h = reader.headers().expect("Could not read header");
        assert_eq!(h[0].to_string(), "timestamp");

        let actual: Vec<String> = h.iter().skip(1).map(|s| s.to_string()).collect();
        assert_eq!(actual, self.header, "Header mismatch");

        let rows: Vec<Row> = reader.records().map(|r| {
            let r = r.expect("Could not read record");
            let time = r.get(0).expect("Could not read time")
                .parse().expect("Could not parse time");
            let values = r.iter().skip(1)
                .map(|s| s.parse().expect("Could not parse value"))
                .collect();
            Row { time, values }
        }).collect();

        self.rows.extend(rows);
        reader
    }

    pub fn write<W: io::Write>(&self, mut writer: Writer<W>) -> Writer<W> {
        let mut h = self.header.iter().map(|s| s.as_str()).collect::<Vec<_>>();
        h.insert(0, "timestamp");

        writer.write_record(h).expect("Failed to write headers");
        let terminator = None::<&[u8]>;
        for row in &self.rows {
            writer.write_field(row.time.to_rfc3339()).expect("Failed to write time");
            for value in row.values.iter() {
                writer.write_field(value.to_string()).expect("Failed to write value");
            }
            writer.write_record(terminator).expect("Failed to write terminator");
        }
        writer.flush().expect("Failed to flush");
        writer
    }

    pub fn merge(&mut self, name: String, samples: &[Sample]) {
        let j = self.header.iter().position(|s| name.eq(s))
            .expect("Could not find column");

        for sample in samples.iter() {
            let time = Utc.timestamp_millis_opt((sample.timestamp() * 1000.0) as i64).unwrap();
            let i = self.rows.iter().position(|r| r.time >= time);
            if let Some(i) = i {
                let r = &mut self.rows[i];
                if r.time == time {
                    r.values[j] = sample.value();
                } else {
                    let mut values = vec![0.0; self.header.len()];
                    values[j] = sample.value();
                    self.rows.insert(i, Row { time, values });
                }
            } else {
                let mut values = vec![0.0; self.header.len()];
                values[j] = sample.value();
                self.rows.push(Row { time, values });
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use std::error::Error;
    use chrono::{TimeZone, Utc};
    use prometheus_http_query::response::Sample;
    use crate::archive::{Archive, Row};

    #[test]
    fn test_read() {
        let header = "timestamp,serviceA-uptime,serviceB-uptime,serviceA-completeness".to_string();
        let h = header.split(',').map(|s| s.to_string()).skip(1).collect();
        let mut archive = Archive::new(h);
        let data = format!(r#"{}
2022-10-27T00:00:00+00:00,100,100,100
2022-10-28T00:00:00+00:00,100,100,100
2022-10-29T00:00:00+00:00,100,100,100
2022-10-30T00:00:00+00:00,100,100,100.00000115780942
2022-10-31T00:00:00+00:00,100,100,100
2022-11-01T00:00:00+00:00,100,100,100
2022-11-02T00:00:00+00:00,100,100,100
2022-11-03T00:00:00+00:00,100,100,100
"#, header);
        let reader = csv::Reader::from_reader(data.as_bytes());
        archive.read(reader);
        assert_eq!(archive.rows.len(), 8);
    }

    #[test]
    fn test_merge() {
        let mut archive = Archive::new(vec!["a".to_string(), "b".to_string()]);
        assert!(archive.rows.is_empty());
        assert_eq!(archive.header, vec!["a", "b"]);

        let mut data = r#"[
            [1666211730.961, "100"],
            [1666298130.961, "99.9"],
            [1666384530.961, "100.1"]
        ]"#;
        let mut samples: Vec<Sample> = serde_json::from_str(data).unwrap();
        archive.merge("a".to_string(), &samples);

        data = r#"[
            [1666211730.961, "99.9"],
            [1666298130.961, "100.1"],
            [1666384530.961, "99.9"]
        ]"#;
        samples = serde_json::from_str(data).unwrap();
        archive.merge("b".to_string(), &samples);

        assert_eq!(archive.rows.len(), samples.len());
    }

    #[test]
    fn test_write() -> Result<(), Box<dyn Error>> {
        let mut archive = Archive::new(vec!["a".to_string(), "b".to_string()]);
        archive.rows.push(Row {
            // https://www.epochconverter.com/
            time: Utc.timestamp_millis_opt(1667477789123).unwrap(),
            values: vec![100.0, 99.0],
        });

        let mut writer = csv::Writer::from_writer(vec![]);
        writer = archive.write(writer);

        let data = String::from_utf8(writer.into_inner()?)?;
        assert_eq!(data, "timestamp,a,b\n2022-11-03T12:16:29.123+00:00,100,99\n");
        Ok(())
    }

}
