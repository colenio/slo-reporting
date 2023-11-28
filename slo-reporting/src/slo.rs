use std::fmt::{Display, Formatter};
use std::time::Duration;
use chrono::{DateTime, Utc};
use prometheus_http_query::Client;
use prometheus_http_query::response::RangeVector;
use serde_derive::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Clone)]
pub struct Objective {
    pub name: String,
    pub display_name: String,
    #[serde(default)]
    pub query: String,
    #[serde(default)]
    pub goal: f64,
    #[serde(with = "humantime_serde")]
    pub rolling_period: Duration,
    #[serde(with = "humantime_serde")]
    pub calendar_period: Duration,
    #[serde(with = "humantime_serde")]
    pub step: Duration,
    #[serde(default)]
    pub create_time: Option<DateTime<Utc>>,
    #[serde(default)]
    pub update_time: Option<DateTime<Utc>>,
}

impl Display for Objective {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "'{}' (goal={}%, rolling={}, step={})", self.name, self.goal,
            humantime::format_duration(self.rolling_period),
            humantime::format_duration(self.step))
    }
}

impl Objective {
    pub async fn range_of(&self, client: &Client, to: Option<DateTime<Utc>>) -> Result<RangeVector, prometheus_http_query::Error> {
        let safe_to = Self::midnight(to).timestamp();
        let from = safe_to - self.rolling_period.as_secs() as i64;
        let step = self.step.as_secs() as f64;
        let response = client
            .query_range(self.query.clone(), from, safe_to, step)
            .get().await?;
        assert!(response.data().as_matrix().is_some());
        let result = response.data().as_matrix()
            .expect("Failed to get result")
            .first().unwrap();
        Ok(result.clone())
    }

    fn midnight(to: Option<DateTime<Utc>>) -> DateTime<Utc> {
        let safe_to = to.unwrap_or_else(Utc::now);
        let mut result = safe_to.date().and_hms(0, 0, 0);
        if result > safe_to {
            result -= chrono::Duration::days(1);
        }
        result
    }
}
