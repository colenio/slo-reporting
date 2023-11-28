use config::{Config, Environment, File};
use prometheus_http_query::{Client, Error};
use serde_derive::{Deserialize, Serialize};
use crate::slo::Objective;

#[derive(Default, Deserialize, Serialize, Clone)]
pub struct Settings {
    pub prometheus: String,
    pub archive: String,
    pub slo: Vec<Objective>,
}

impl Settings {
    pub fn new() -> Self {
        let s = Config::builder()
            .add_source(File::with_name("config/settings.yaml").required(true))
            .add_source(Environment::default())
            .build().expect("Failed to build config");
        s.try_deserialize().expect("Failed to deserialize config")
    }

    pub(crate) fn client_of(&self) -> Result<Client, Error> {
        Client::try_from(self.prometheus.clone())
    }
}

#[derive(Default, Deserialize, Serialize, Clone)]
pub struct PrometheusSettings {
    pub endpoint: String,
}

#[cfg(test)]
mod tests {
    use crate::settings::Settings;

    #[test]
    fn test_settings() {
        let s = Settings::new();
        assert_eq!(s.prometheus, "http://localhost:9090");
    }
}
