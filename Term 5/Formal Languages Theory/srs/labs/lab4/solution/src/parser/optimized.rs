use crate::parser::Parser;

pub struct OptimizedParser;

// ((b | a\3) | (a \2\2))*

impl Parser for OptimizedParser {
    fn parse(input: &str) -> bool {
        if !OptimizedParser::lookahead(input) {
            return false;
        }

        let bytes = input.as_bytes();
        let mut slash_2 = String::from("b");
        let mut slash_3 = String::new();

        let mut i = 1;
        while i < bytes.len() {
            // println!("At position {}: slash_2='{}', slash_3='{}'", &input[i..], slash_2, slash_3);
            
            // We can consume only bb
            if bytes[i] == b'b' {
                if bytes.len() > i + 1 && bytes[i + 1] == b'b' {
                    i += 2;
                    slash_2 = String::from("b");
                } else {
                    return false;
                }
            } else if bytes[i] == b'a' {
                let current_slash_2 = format!("a{}", slash_3);
                let current_slash_3 = format!("a{}{}", slash_2, slash_2);

                // Try to consume a \3
                if slash_3 != "" && input[i..].starts_with(current_slash_2.as_str()) {
                    i += current_slash_2.len();
                    slash_2 = current_slash_2;
                }
                // Try to consume a \2\2
                else if slash_2 != "" && input[i..].starts_with(current_slash_3.as_str()) {
                    i += current_slash_3.len();
                    slash_3 = current_slash_3;
                } else {
                    return false;
                }
            } else {
                return false;
            }
        }

        return true;
    }
}
