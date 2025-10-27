import click
from scrapers.base_scraper import BaseScraper
from etl.base_etl import BaseETL
from analytics.base_model import BaseMLModel
from etl.pipelines.vehicle_etl_pipeline import VehicleETLPipeline

@click.group()
def cli():
    """Data Pipeline CLI"""
    pass

@cli.command()
@click.option('--scraper', required=True, help='Scraper name to run')
def scrape(scraper):
    """Run a specific scraper"""
    click.echo(f"Running scraper: {scraper}")
    # Import and run specific scraper

@cli.command()
@click.option('--pipeline', default='vehicle', help='ETL pipeline to run')
@click.option('--mode', type=click.Choice(['full', 'incremental']), default='full', help='ETL mode')
@click.option('--hours', default=24, help='Hours for incremental ETL')
def etl(pipeline, mode, hours):
    """Run ETL pipeline"""
    if pipeline == 'vehicle':
        etl_pipeline = VehicleETLPipeline()
        if mode == 'full':
            click.echo("Running full ETL pipeline...")
            stats = etl_pipeline.run_full_pipeline()
            click.echo(f"Processed {stats['total_records']} records")
        else:
            click.echo(f"Running incremental ETL for last {hours} hours...")
            etl_pipeline.run_incremental_pipeline(hours)
    else:
        click.echo(f"Unknown pipeline: {pipeline}")

@cli.command()
@click.option('--model', required=True, help='ML model to train/predict')
@click.option('--action', type=click.Choice(['train', 'predict']), required=True)
def ml(model, action):
    """Train or run ML model predictions"""
    click.echo(f"{action.capitalize()}ing model: {model}")
    # Import and run specific ML model

if __name__ == '__main__':
    cli()