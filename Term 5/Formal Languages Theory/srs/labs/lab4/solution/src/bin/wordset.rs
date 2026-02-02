use rand::prelude::*;
use solution::constants::*;
use solution::parser::Parser;
use solution::parser::optimized::OptimizedParser;
use std::fs::File;
use std::io::prelude::*;
use std::path::PathBuf;

fn sample_tokens<R: rand::Rng + ?Sized>(rng: &mut R, tokens: &[&str]) -> String {
    let mut out = String::new();
    for _ in 0..rng.random_range(MIN_WORD_LEN..=MAX_WORD_LEN) {
        out.push_str(tokens.choose(rng).unwrap());
    }
    out
}

fn main() -> std::io::Result<()> {
    let base_path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));

    let folder_path = base_path.join(WORDSET_FOLDERNAME);
    if !folder_path.exists() {
        std::fs::create_dir_all(&folder_path)?;
    }

    // Random words
    let rng = rand::rng();
    let random_path = folder_path.join(RANDOM_WORDS_FILENAME);
    let mut file = File::create(random_path).unwrap();
    for _ in 0..NUM_WORDS {
        let word = sample_tokens(&mut rng.clone(), &["a", "b"]);
        writeln!(file, "{}", word).unwrap();
    }
    println!("Random words created: {}", RANDOM_WORDS_FILENAME);

    // Good words
    let mut file = File::create(folder_path.join(GOOD_WORDS_FILENAME)).unwrap();
    let mut words_added = 0;
    while words_added < NUM_WORDS {
        // force first char to be "b"
        let word = "b".to_string() + &sample_tokens(&mut rng.clone(), &["a", "bb"])[1..];

        if OptimizedParser::parse(&word) {
            writeln!(file, "{}", word).unwrap();
            words_added += 1;
        }
    }

    println!("Good words created: {}", GOOD_WORDS_FILENAME);

    // Bad words
    let mut file = File::create(folder_path.join(BAD_WORDS_FILENAME)).unwrap();
    let mut words_added = 0;
    while words_added < NUM_WORDS {
        let word = sample_tokens(&mut rng.clone(), &["a", "b"]);
        if !OptimizedParser::parse(&word) {
            writeln!(file, "{}", word).unwrap();
            words_added += 1;
        }
    }
    println!("Bad words created: {}", BAD_WORDS_FILENAME);
    Ok(())
}
