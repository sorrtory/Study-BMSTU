pub const MAX_STRING_LENGTH: usize = 16;
pub const NUM_TEST_STRINGS: usize = 10;
pub const ALPHABET: &[char] = &['a', 'b', 'c'];

// Note: regex crate requires ^ and $ for full match
pub const REGEX_PATTERN: &str = "^((aa|ab|cc)*aba(aaa|bcc)*)*((abac|(cc)*)(b|ca))*$";
pub const EXTENDED_REGEX_PATTERN: &str = "^((((a[ab]|cc)+)?aba((aaa|bcc)+)?)+)?(((abac|((cc)+)?)(b|ca))+)?$";
