use config::{Config, Environment, File};
use prometheus_http_query::{Client, Error};
use serde_derive::{Deserialize, Serialize};
use crate::slo::Objective;

#[derive(Default, Deserialize, Serialize, Clone)]
pub struct Settings {
    #[serde(default = "Settings::default_prometheus_url")]
    pub prometheus: String,
    #[serde(default = "Settings::default_archive_path")]
    pub archive: String,
    pub slo: Vec<Objective>,
}

impl Settings {
    pub fn new() -> Self {
        let c = Config::builder()
            .add_source(File::with_name("config/settings.yaml").required(true))
            .add_source(Environment::default())
            .build().expect("Failed to build config");
        c.try_deserialize().expect("Failed to deserialize config")
    }

    pub(crate) fn client_of(&self) -> Result<Client, Error> {
        Client::try_from(self.prometheus.clone())
    }

    fn default_prometheus_url() -> String{String::from("http://localhost:9090")}
    fn default_archive_path() -> String{String::from("./data/slo-reporting.csv")}
}

#[cfg(test)]
mod tests {
    use config::{Config, FileFormat};
    use crate::settings::Settings;
    use crate::slo::Objective;

    #[test]
    fn test_settings() {
        let s = Settings::new();
        assert_eq!(s.prometheus, "http://localhost:9090");
    }

    #[test]
    fn test_defaults() {
        let yaml = "slo: [{name: slo, query: promql}]";
        let c = Config::builder()
            .add_source(config::File::from_str(yaml, FileFormat::Yaml))
            .build().expect("Failed to build config");
        let s = c.try_deserialize::<Settings>().expect("Failed to deserialize config");
        assert_eq!(s.prometheus, Settings::default_prometheus_url());
        assert_eq!(s.archive, Settings::default_archive_path());
        assert_eq!(s.slo.len(), 1);
        let slo = s.slo.get(0).unwrap();
        assert_eq!(slo.name, "slo");
        assert_eq!(slo.goal, Objective::default_goal());
        assert_eq!(slo.rolling_period, Objective::default_rolling_period());
        assert_eq!(slo.calendar_period, Objective::default_calendar_period());
        assert_eq!(slo.step, Objective::default_step());
    }
}
