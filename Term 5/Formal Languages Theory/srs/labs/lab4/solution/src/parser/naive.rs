use crate::parser::Parser;

pub struct NaiveParser;

// ((b | a\3) | (a \2\2))*

fn parse_step(input: &str, slash_2: &str, slash_3: &str) -> bool {
    // println!("Parsing step: input='{}', \\2='{}', \\3='{}'", input, slash_2, slash_3);

    // If we consumed all input, we are ok
    if input.is_empty() {
        return true;
    }

    // Prepare current acceptable patterns
    let current_slash_2 = format!("a{}", slash_3);
    let current_slash_3 = format!("a{}{}", slash_2, slash_2);


    let bytes = input.as_bytes();
    let mut result = false;

    // b

    // Consume "b" and update slash_2
    if bytes[0] == b'b' {
        result = result || parse_step(input[1..].as_ref(), "b", slash_3);
    }



    if bytes[0] == b'a' {
        // | a \3
        if slash_3 != "" && input.starts_with(current_slash_2.as_str()) {
            result = result || parse_step(&input[current_slash_2.len()..], current_slash_2.as_str(), slash_3);
        }

        // | a \2\2
        if slash_2 != "" && input.starts_with(current_slash_3.as_str()) {
            result = result || parse_step(&input[current_slash_3.len()..], slash_2, current_slash_3.as_str());
        }
    }

    result

}

impl Parser for NaiveParser {


    fn parse(input: &str) -> bool {
        if !NaiveParser::lookahead(input) {
            return false;
        }

        // Start recursive parsing with b consumed
        parse_step(input.as_ref(), "", "")
    }    
}