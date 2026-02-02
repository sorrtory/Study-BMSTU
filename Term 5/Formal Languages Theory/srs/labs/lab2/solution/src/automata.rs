pub mod dfa;
pub mod nfa;
pub mod afa;

use std::collections::HashMap;
use std::collections::VecDeque;
use std::fmt;

const EPSILON: char = 'ε';

pub struct State {
    pub name: String,
    pub index: usize,
    pub is_final: bool,
    pub transitions: HashMap<char, Vec<usize>>, // (input symbol, next state index)
}

impl State {
    pub fn new(name: &str, index: usize, is_final: bool) -> Self {
        State {
            name: name.to_string(),
            index,
            is_final,
            transitions: HashMap::new(),
        }
    }

    pub fn add_transition(&mut self, input: char, next_state_index: Vec<usize>) {
        self.transitions.insert(input, next_state_index);
    }
}

pub struct Automata {
    pub initial_state_index: usize,
    pub states: Vec<State>,
}

impl Automata {
    pub fn new() -> Self {
        Automata {
            states: Vec::new(),
            initial_state_index: 0,
        }
    }

    fn add_state(&mut self, state: State) {
        self.states.push(state);
    }

    // BFS-based NFA recognition
    pub fn can_recognize(&self, input: &str) -> bool {
        // BFS to handle NFA transitions
        let mut queue: VecDeque<usize> = VecDeque::new();
        queue.push_back(self.initial_state_index);

        for symbol in input.chars() {
            let mut next_queue: VecDeque<usize> = VecDeque::new();

            // Handle transitions for the current symbol
            while let Some(state_index) = queue.pop_front() {
                let state = &self.states[state_index];

                // Check for epsilon transitions
                if let Some(epsilon_states) = state.transitions.get(&EPSILON) {
                    for &eps_state_index in epsilon_states {
                        next_queue.push_back(eps_state_index);
                    }
                }

                // Get next states for the current symbol
                if let Some(next_state_indices) = state.transitions.get(&symbol) {
                    for &next_state_index in next_state_indices {
                        next_queue.push_back(next_state_index);
                    }
                }
            }

            // If we can't move to any state with the current symbol
            if next_queue.is_empty() {
                return false;
            }

            // Move to the next set of states
            queue = next_queue;
        }

        // Check if any of the resulting states is a final state
        queue
            .iter()
            .any(|&state_index| self.states[state_index].is_final)
    }
}

// Interface for Automata types
pub trait IAutomata {
    fn new() -> Self;
    fn init_transitions(&mut self); // init transitions
    fn can_recognize(&self, input: &str) -> bool;
}

// --- Debug implementations ---

impl fmt::Debug for State {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("State")
            .field("name", &self.name)
            .field("index", &self.index)
            .field("is_final", &self.is_final)
            .field("transitions", &self.transitions)
            .finish()
    }
}

impl fmt::Debug for Automata {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("Automata")
            .field("initial_state_index", &self.initial_state_index)
            .field("states", &self.states)
            .finish()
    }
}
