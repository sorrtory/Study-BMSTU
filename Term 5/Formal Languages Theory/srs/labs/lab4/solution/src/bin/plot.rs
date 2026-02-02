use plotters::prelude::*;

use solution::constants::*;
use std::io::{BufRead, BufReader};
use std::path::PathBuf;

fn draw(
    wordset_path: &std::path::Path,
    plot_file: &std::path::Path,
) -> Result<(), Box<dyn std::error::Error>> {
    let wordset_file = std::fs::File::open(wordset_path)?;
    let wordset_buffer = BufReader::new(wordset_file);
    let mut random_data: Vec<(String, bool, u128, u128)> = Vec::new();
    for line in wordset_buffer.lines() {
        let line = line?;
        let parts: Vec<&str> = line.split(',').collect();
        if parts.len() != 4 {
            continue;
        }
        let word = parts[0];
        let result_str = parts[1];

        // as nanos
        let naive_time_str = parts[2];
        let optimized_time_str = parts[3];

        // println!("Word: {}, Naive time: {}, Optimized time: {}", word, naive_time_str, optimized_time_str);
        let naive_time: u128 = naive_time_str.parse().unwrap_or(0);
        let optimized_time: u128 = optimized_time_str.parse().unwrap_or(0);
        let result: bool = result_str.parse().unwrap_or(false);
        random_data.push((word.to_string(), result, naive_time, optimized_time));
    }

    // Draw
    let root = BitMapBackend::new(plot_file, PLOT_SIZE).into_drawing_area();
    root.fill(&WHITE);
    let root = root.margin(10, 10, 10, 10);
    let mut chart = ChartBuilder::on(&root)
        .caption("Random Words Parsing Time", ("sans-serif", 40).into_font())
        .x_label_area_size(40)
        .y_label_area_size(60)
        .build_cartesian_2d(0f32..MAX_WORD_LEN as f32, 0f32..MAX_WORD_PARSE_TIME_PLOT as f32)?;

    // Then we can draw a mesh
    chart
        .configure_mesh()
        // We can customize the maximum number of labels allowed for each axis
        .x_labels(5)
        .y_labels(5)
        // We can also change the format of the label text
        .y_label_formatter(&|x| format!("{:.0}", x))
        .x_label_formatter(&|x| format!("{:.0}", x))
        .x_desc("Word Length")
        .y_desc("Time (nanoseconds)")
        .draw()?;

    let size = 2;
    // Naive: Red
    chart
        .draw_series(
            random_data
                .iter()
                .map(|word| Circle::new((word.0.len() as f32, word.2 as f32), size, RED.filled())),
        )
        .unwrap();

    // Optimized: Blue
    chart
        .draw_series(
            random_data
                .iter()
                .map(|word| Circle::new((word.0.len() as f32, word.3 as f32), size, BLUE.filled())),
        )
        .unwrap();
    root.present()?;
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let base_path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let folder_path = base_path.join(WORDSET_FOLDERNAME);

    // Random words
    let wordset_path = folder_path.join(RANDOM_WORDS_DUMP);
    let plot_file = folder_path.join(RANDOM_WORDS_PLOT);
    draw(&wordset_path, &plot_file)?;

    // Good words
    let wordset_path = folder_path.join(GOOD_WORDS_DUMP);
    let plot_file = folder_path.join(GOOD_WORDS_PLOT);
    draw(&wordset_path, &plot_file)?;

    // Bad words
    let wordset_path = folder_path.join(BAD_WORDS_DUMP);
    let plot_file = folder_path.join(BAD_WORDS_PLOT);
    draw(&wordset_path, &plot_file)?;

    Ok(())
}
