mod automata;
mod constants;

use constants::*;

use fancy_regex::Regex;
use automata::IAutomata;
use automata::dfa::DFA;
use automata::nfa::NFA;
use automata::afa::AFA;

use rand::Rng;

fn generate_random_string() -> String {
    let mut rng = rand::rng();

    let length = rng.random_range(1..=MAX_STRING_LENGTH);

    (0..length)
        .map(|_| {
            let idx = rng.random_range(0..ALPHABET.len());
            ALPHABET[idx]
        })
        .collect()
}

fn main() {
    let mut dfa = DFA::new();
    dfa.init_transitions();

    let mut nfa = NFA::new();
    nfa.init_transitions();

    let mut afa = AFA::new();
    afa.init_transitions();

    let mut bad = false;
    for _ in 0..NUM_TEST_STRINGS {
        let test_str = generate_random_string();
        println!("Testing string: {}", test_str);

        // Regex match
        let regex_matches = Regex::new(REGEX_PATTERN)
            .unwrap()
            .is_match(&test_str).unwrap();
        let extended_regex_matches = Regex::new(EXTENDED_REGEX_PATTERN)
            .unwrap()
            .is_match(&test_str).unwrap();

        // Automata recognition
        let dfa_recognizes = dfa.can_recognize(&test_str);
        let nfa_recognizes = nfa.can_recognize(&test_str);
        let afa_recognizes = afa.can_recognize(&test_str);

        let all_true = regex_matches && extended_regex_matches && dfa_recognizes && nfa_recognizes && afa_recognizes;
        let all_false =
            !regex_matches && !extended_regex_matches && !dfa_recognizes && !nfa_recognizes && !afa_recognizes;
        if !(all_true || all_false) {
            println!("Discrepancy found for string: {}", test_str);
            println!("Regex matches: {}", regex_matches);
            println!("Extended regex matches: {}", extended_regex_matches);
            println!("DFA recognizes: {}", dfa_recognizes);
            println!("NFA recognizes: {}", nfa_recognizes);
            println!("AFA recognizes: {}", afa_recognizes);
            bad = true;
            break;
        }
    }

    if bad {
        println!("Bad news!");
    } else {
        println!("All good!");
    }
}
