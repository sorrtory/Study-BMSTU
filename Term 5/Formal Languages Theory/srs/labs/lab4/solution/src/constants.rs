// Filenames
pub const WORDSET_FOLDERNAME: &str = "wordsets/";

// Random words
pub const RANDOM_WORDS_FILENAME: &str = "random.txt";
pub const RANDOM_WORDS_DUMP: &str = "random.dump";
pub const RANDOM_WORDS_PLOT: &str = "random.png";

// 100% accepting words
pub const GOOD_WORDS_FILENAME: &str = "good.txt";
pub const GOOD_WORDS_DUMP: &str = "good.dump";
pub const GOOD_WORDS_PLOT: &str = "good.png";

// 0% accepting words
pub const BAD_WORDS_FILENAME: &str = "bad.txt";
pub const BAD_WORDS_DUMP: &str = "bad.dump";
pub const BAD_WORDS_PLOT: &str = "bad.png";

// Wordset parameters
pub const ALPHABET: &str = "ab";
pub const NUM_WORDS: usize = 100;
pub const MIN_WORD_LEN: usize = 10;
pub const MAX_WORD_LEN: usize = 100;
pub const MAX_WORD_PARSE_TIME_PLOT: u128 = 5000; // in nanoseconds

// Plot parameters
pub const PLOT_SIZE: (u32, u32) = (640, 480);