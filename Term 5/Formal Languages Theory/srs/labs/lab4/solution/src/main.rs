use std::fs::File;
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::time::Duration;

use rand::rand_core::le;
use solution::constants::*;
use solution::parser::Parser;
use solution::parser::naive::NaiveParser;
use solution::parser::optimized::OptimizedParser;

fn run<T: Parser>(word: &str) -> (bool, Duration) {
    let time_start = std::time::Instant::now();
    let parse_result = T::parse(word);
    let time_end = std::time::Instant::now();
    let duration = time_end.duration_since(time_start);

    return (parse_result, duration);
}

fn fuzz(wordset_file: &std::path::Path, output_file: &std::path::Path) {
    // Open output file
    let write_file = File::create(output_file).expect("Failed to create output file");
    let mut write_buf = BufWriter::new(write_file);

    // Open read file
    let file = File::open(wordset_file).expect("Failed to open wordset file");
    let reader = BufReader::new(file);
    for line in reader.lines() {
        let word = line.expect("Failed to read line");
        let (naive_result, naive_duration) = run::<NaiveParser>(&word);
        let (optimized_result, optimized_duration) = run::<OptimizedParser>(&word);

        // Check for discrepancies
        if naive_result != optimized_result {
            panic!(
                "Discrepancy found for word '{}': Naive result = {}, Optimized result = {}",
                word, naive_result, optimized_result
            );
        } else {
            // println!("Word '{}': Result = {}, Naive time = {:?}, Optimized time = {:?}", word, naive_result, naive_duration, optimized_duration);
            // check out order.
            writeln!(
                write_buf,
                "{},{},{:?},{:?}",
                word,
                naive_result,
                naive_duration.as_nanos(),
                optimized_duration.as_nanos()
            )
            .expect("Failed to write to output file");
        }
    }
}

fn main() {
    // let word = "bbbbbbbabbaabb";
    // let (naive_result, naive_duration) = run::<NaiveParser>(word);
    // let (optimized_result, optimized_duration) = run::<OptimizedParser>(word);
    // println!("Word '{}': Naive result = {}, time = {:?}; Optimized result = {}, time = {:?}", word, naive_result, naive_duration, optimized_result, optimized_duration);
    // return;

    // Open random words file
    let base_path = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let folder_path = base_path.join(WORDSET_FOLDERNAME);

    // Random words
    let wordset_file = folder_path.join(RANDOM_WORDS_FILENAME);
    let output_file = folder_path.join(RANDOM_WORDS_DUMP);
    fuzz(&wordset_file, &output_file);

    // Good words
    let wordset_file = folder_path.join(GOOD_WORDS_FILENAME);
    let output_file = folder_path.join(GOOD_WORDS_DUMP);
    fuzz(&wordset_file, &output_file);

    // Bad words
    let wordset_file = folder_path.join(BAD_WORDS_FILENAME);
    let output_file = folder_path.join(BAD_WORDS_DUMP);
    fuzz(&wordset_file, &output_file);
}
