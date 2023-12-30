mod settings;
mod slo;
mod archive;


use std::fs::create_dir_all;
use std::path::Path;
use csv::{Reader, Writer};
use env_logger::{Target, WriteStyle};
use settings::Settings;
use prometheus_http_query::{Error};
use archive::Archive;


#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Error> {
    const PKG_NAME: &str = env!("CARGO_PKG_NAME");
    let pkg_version: &str = option_env!("BUILD_VERSION").unwrap_or("dev");

    env_logger::Builder::from_default_env()
        .target(Target::Stdout)
        .write_style(WriteStyle::Always)
        .init();

    log::info!("Started {}, version {}", PKG_NAME, pkg_version);

    let settings = Settings::new();

    let header = settings.slo.iter().map(|s| s.name.clone()).collect();
    let mut archive = Archive::new(header);
    let reader = Reader::from_path(&settings.archive);
    if reader.is_ok() {
        archive.read(reader.unwrap());
        log::info!("Read '{}'", settings.archive);
    }

    let client = settings.client_of()
        .expect("Failed to create Prometheus client");

    for slo in settings.slo {
        log::debug!("Processing {}", slo);
        let result = slo.range_of(&client, None)
            .await
            .expect("Failed to get range");
        log::info!("Processed {}", slo);

        archive.merge(slo.name, result.samples());
        log::debug!("Merged {} samples", result.samples().len());
    }

    let dir = Path::new(&settings.archive).parent().unwrap();
    create_dir_all(dir).expect("Could not create output directory");
    let writer = Writer::from_path(&settings.archive)
        .expect("Failed to open archive");
    archive.write(writer);
    log::info!("Wrote '{}'", settings.archive);

    Ok(())
}
