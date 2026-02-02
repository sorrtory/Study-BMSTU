use std::collections::{HashSet, VecDeque};

use solution::srs::{Rule, SRS, ShortLexString, TString, Term};

fn main() {
    const ABC: [&str; 3] = ["a", "b", "c"]; // Moves
    const DEPTH: usize = 5; // Recursion depth

    // Initial SRS
    let mut s = SRS::<ShortLexString>::new();
    s.add_rule("aabc", "bbaa");
    s.add_rule("b", "ccaa");
    s.add_rule("bc", "a");
    s.add_rule("aac", "");

    // New KB rules
    s.add_rule("c", "b");
    s.add_rule("ac", "ab");
    s.add_rule("ba", "ab");
    s.add_rule("bb", "a");
    s.add_rule("ca", "ab");
    s.add_rule("cb", "a");
    s.add_rule("aaa", "b");
    s.add_rule("aab", "");
    s.add_rule("caa", "aab");
    s.add_rule("cab", "aa");
    s.add_rule("cca", "cab");
    s.add_rule("ccb", "ca");
    s.add_rule("aaaa", "ab");
    s.add_rule("aaab", "a");
    s.add_rule("acaa", "bb");
    s.add_rule("ccab", "aab");
    s.add_rule("aaaaa", "aab");
    s.add_rule("aaaab", "aa");
    s.add_rule("aaaaab", "aaa");

    s.balance_all();
    s.sort();
    println!("Initial SRS: {:?}", s);

    // Minimalize SRS

    let mut normal_forms = HashSet::<ShortLexString>::new();
    let mut to_process = VecDeque::<ShortLexString>::new();

    // Start from the empty string
    let empty = ShortLexString::new("");
    to_process.push_back(empty);

    while let Some(word) = to_process.pop_back() {
        if word.as_str().len() >= DEPTH {
            continue;
        }
        // Append each letter from the alphabet
        for t in ABC.iter() {
            let mut new_word = word.clone().as_str().to_string();
            new_word.push_str(t);
            let new_word = ShortLexString::new(new_word.as_str());

            // Calculate normal forms for this new word
            let nfs = s.get_normal_forms(&new_word, 100).unwrap();
            for nf in nfs {
                if !normal_forms.contains(&nf) {
                    normal_forms.insert(nf.clone());
                    if nf.as_str().len() < DEPTH {
                        to_process.push_back(nf);
                    }
                }
            }
        }
        println!(
            "Processed word {:?}, total normal forms found: {}\n",
            word,
            normal_forms.len()
        );
    }

    println!(
        "Total normal forms up to length {}: {}",
        DEPTH,
        normal_forms.len()
    );
    println!("RESULTING NORMAL FORMS {:?}", normal_forms);

    // Minimize
    let empty = ShortLexString::new("");
    to_process.push_back(empty);
    while let Some(word) = to_process.pop_back() {
        if word.as_str().len() >= DEPTH {
            continue;
        }
        // Append each letter from the alphabet
        for t in ABC.iter() {
            let mut new_word = word.clone().as_str().to_string();
            new_word.push_str(t);
            let new_word = ShortLexString::new(new_word.as_str());

            // Calculate normal forms for this new word
            let nfs = s.get_normal_forms(&new_word, 100).unwrap();
            for nf in nfs {
                if normal_forms.contains(&nf) {
                    println!("WORD {:?} REDUCES TO NORMAL FORM {:?}", new_word, nf);
                } else {
                    panic!("FOUND NEW NORMAL FORM DURING MINIMIZATION!");
                }
            }

            if new_word.as_str().len() < DEPTH {
                to_process.push_back(new_word);
            }
        }
    }
}
