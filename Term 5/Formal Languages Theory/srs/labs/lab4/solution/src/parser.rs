pub mod naive;
pub mod optimized;

pub trait Parser {
    fn parse(input: &str) -> bool;

    // O(n): follow up pattern
    fn lookahead(input: &str) -> bool {
        // hardcode: b(a|bb)*$
        let bytes = input.as_bytes();
        let n = bytes.len();

        // check first char to be "b"
        if input.is_empty() || bytes[0] != b'b' {
            return false;
        }
        let mut last_was_single_b = false;
        for i in 1..n {
            if bytes[i] == b'a' {
                // accept only "bb"
                if last_was_single_b {
                    return false;
                }
                last_was_single_b = false;
            } else if bytes[i] == b'b' {
                if last_was_single_b {
                    last_was_single_b = false;
                } else {
                    last_was_single_b = true;
                }
            } else {
                return false;
            }
        }
        // should not end with single "b"
        if last_was_single_b {
            return false;
        }
        true
    }
}
