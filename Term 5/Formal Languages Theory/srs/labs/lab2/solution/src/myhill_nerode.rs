mod automata;
mod constants;

use automata::IAutomata;
use automata::afa::*;
use automata::dfa::DFA;
use automata::nfa::NFA;

use constants::*;
use std::collections::{HashSet, VecDeque};

/// Generate *all* suffixes over `alphabet` with length in [0, max_len].
/// ε (empty string) is included as the first element.
fn generate_all_suffixes(alphabet: &[char], max_len: usize) -> Vec<String> {
    let mut res = Vec::new();
    res.push(String::new()); // epsilon string

    if alphabet.is_empty() || max_len == 0 {
        return res;
    }

    fn build_for_len(
        alphabet: &[char],
        target_len: usize,
        cur: &mut String,
        out: &mut Vec<String>,
    ) {
        if cur.len() == target_len {
            out.push(cur.clone());
            return;
        }

        for &ch in alphabet {
            cur.push(ch);
            build_for_len(alphabet, target_len, cur, out);
            cur.pop();
        }
    }

    for len in 1..=max_len {
        let mut cur = String::with_capacity(len);
        build_for_len(alphabet, len, &mut cur, &mut res);
    }

    res
}

/// Build the 0/1 matrix:
/// rows = prefixes (states), columns = suffixes.
/// cell[i][j] = 1 iff prefix_i + suffix_j is accepted (within MAX_STRING_LENGTH).
fn build_signature_matrix(
    automata: &automata::Automata,
    prefixes: &[String],
    suffixes: &[String],
) -> Vec<Vec<u8>> {
    let mut matrix = vec![vec![0u8; suffixes.len()]; prefixes.len()];

    for (i, prefix) in prefixes.iter().enumerate() {
        for (j, suffix) in suffixes.iter().enumerate() {
            let combined = format!("{}{}", prefix, suffix);

            if combined.len() > MAX_STRING_LENGTH {
                panic!("combined string too long: {}", combined);
            } else if automata.can_recognize(&combined) {
                matrix[i][j] = 1;
            } else {
                matrix[i][j] = 0;
            }
        }
    }

    matrix
}

/// Myhill–Nerode stopping condition:
/// - all rows (0/1 patterns) are pairwise distinct
fn myhill_nerode_done(matrix: &[Vec<u8>]) -> bool {
    // hashset + slice comparison for optimization
    let mut seen: HashSet<&[u8]> = HashSet::new();

    for row in matrix {
        let slice: &[u8] = row.as_slice();

        // If we cannot insert, this pattern was already seen -> not done
        if !seen.insert(slice) {
            return false;
        }
    }

    true
}

/// Print a nice markdown table given:
/// - automaton (for state names)
/// - prefixes (one per state)
/// - suffixes (columns)
/// - precomputed signature matrix (0/1 values)
fn print_markdown_table(
    automata: &automata::Automata,
    prefixes: &[String],
    suffixes: &[String],
    matrix: &[Vec<u8>],
) {
    // Header row
    print!("| state | prefix ");
    for s in suffixes {
        let head = if s.is_empty() {
            "ε".to_string()
        } else {
            s.clone()
        };
        print!("| {} ", head);
    }
    println!("|");

    // Separator row
    print!("| ----- | ------ ");
    for _ in suffixes {
        print!("| --- ");
    }
    println!("|");

    // Body: one row per state/prefix
    for (i, prefix) in prefixes.iter().enumerate() {
        let state_name = &automata.states[i].name;
        let prefix_display = if prefix.is_empty() {
            "ε".to_string()
        } else {
            prefix.clone()
        };

        print!("| {} | **{}** ", state_name, prefix_display);

        for &cell in &matrix[i] {
            print!("| {} ", cell);
        }

        println!("|");
    }
}

// BFS to get the shortest words from the initial state to each state
pub fn shortest_words_from_initial(automata: &automata::Automata) -> Vec<Option<String>> {
    let n = automata.states.len();
    let start = automata.initial_state_index;

    // predecessor state and char used to get there
    let mut pred_state: Vec<Option<usize>> = vec![None; n];
    let mut pred_char: Vec<Option<char>> = vec![None; n];

    let mut visited = vec![false; n];
    let mut queue = VecDeque::new();

    visited[start] = true;
    queue.push_back(start);

    while let Some(s) = queue.pop_front() {
        for (&ch, next_states) in &automata.states[s].transitions {
            for &next in next_states {
                if !visited[next] {
                    visited[next] = true;
                    pred_state[next] = Some(s);
                    pred_char[next] = Some(ch);
                    queue.push_back(next);
                }
            }
        }
    }

    // reconstruct minimal word for each state
    let mut result: Vec<Option<String>> = vec![None; n];

    for state in 0..n {
        if state == start {
            // shortest word to reach initial state is empty string
            result[state] = Some(String::new());
            continue;
        }

        if !visited[state] {
            // unreachable
            result[state] = None;
            continue;
        }

        // walk back using predecessors
        let mut chars = Vec::new();
        let mut cur = state;
        while cur != start {
            let p = pred_state[cur].expect("visited node must have predecessor (except start)");
            let c = pred_char[cur].expect("transition char must exist");
            chars.push(c);
            cur = p;
        }
        chars.reverse();
        result[state] = Some(chars.iter().collect());
    }

    result
}

fn main() {
    // Build automata and transitions

    let mut automata = DFA::new();
    // let mut automata = NFA::new();
    // let mut automata = AFA_bcb::new();
    // let mut automata = AFA_suf::new();
    automata.init_transitions();

    // PREFIXES: shortest words from initial state to each state
    let words = shortest_words_from_initial(&automata.automata);
    let mut prefixes = Vec::new();
    for (i, w) in words.iter().enumerate() {
        match w {
            Some(s) => prefixes.push(s.clone()),
            None => panic!("state {i}: unreachable"),
        }
    }

    // Check prefixes to be unique
    let mut seen_prefixes = HashSet::new();
    for prefix in &prefixes.clone() {
        if !seen_prefixes.insert(prefix) {
            println!("Duplicate prefix found: {}", prefix);
            // Remove duplicates by keeping only one occurrence
            prefixes.retain(|p| p != prefix);
            prefixes.push(prefix.clone());
        }
    }

    println!("Prefixes (shortest words to each state):");
    for (i, p) in prefixes.iter().enumerate() {
        println!(
            "  State {}: {}",
            automata.automata.states[i].name,
            if p.is_empty() { "ε" } else { p }
        );
    }

    // Generate all possible suffixes up to MAX_STRING_LENGTH
    let all_suffixes = generate_all_suffixes(ALPHABET, MAX_STRING_LENGTH);
    println!(
        "Generated {} suffixes over alphabet {:?} up to length {}",
        all_suffixes.len(),
        ALPHABET,
        MAX_STRING_LENGTH
    );

    // Now incrementally add suffixes until Myhill–Nerode condition is satisfied
    let mut suffixes: Vec<String> = Vec::new();
    let mut matrix: Vec<Vec<u8>> = Vec::new();

    for s in all_suffixes {
        suffixes.push(s);
        matrix = build_signature_matrix(&automata.automata, &prefixes, &suffixes);

        if myhill_nerode_done(&matrix) {
            break;
        }

        println!(
            "Suffixes used so far: {}, current matrix size: {}x{}",
            suffixes.len(),
            matrix.len(),
            matrix[0].len()
        );
    }

    if !myhill_nerode_done(&matrix) {
        panic!("Myhill–Nerode condition not satisfied after using all suffixes");
    }
    // Finally print the markdown table
    print_markdown_table(&automata.automata, &prefixes, &suffixes, &matrix);
}
