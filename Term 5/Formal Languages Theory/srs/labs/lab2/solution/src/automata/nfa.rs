use crate::automata::{Automata, IAutomata, State};

pub struct NFA {
    pub automata: Automata,
}

impl IAutomata for NFA {
    fn new() -> Self {
        NFA {
            automata: Automata::new(),
        }
    }

    fn init_transitions(&mut self) {
        self.automata.states.clear();

        // Set initial state (dummy -> state 0)
        self.automata.initial_state_index = 0;

        // Create states q0..q18, mark final states 0, 5, 13
        let mut q0 = State::new("q0", 0, true);
        let mut q1 = State::new("q1", 1, false);
        let mut q2 = State::new("q2", 2, false);
        let mut q3 = State::new("q3", 3, false);
        let mut q4 = State::new("q4", 4, false);
        let mut q5 = State::new("q5", 5, true);
        let mut q6 = State::new("q6", 6, false);
        let mut q7 = State::new("q7", 7, false);
        let mut q8 = State::new("q8", 8, false);
        let mut q9 = State::new("q9", 9, false);
        let mut q10 = State::new("q10", 10, false);
        let mut q11 = State::new("q11", 11, false);
        let mut q12 = State::new("q12", 12, false);
        let mut q13 = State::new("q13", 13, true);
        let mut q14 = State::new("q14", 14, false);
        let mut q15 = State::new("q15", 15, false);
        let mut q16 = State::new("q16", 16, false);
        let mut q17 = State::new("q17", 17, false);
        let mut q18 = State::new("q18", 18, false);

        // Transitions according to provided DOT graph
        q0.add_transition('a', vec![1, 2, 3, 4]);
        q0.add_transition('b', vec![5]);
        q0.add_transition('c', vec![6, 7, 8]);

        q1.add_transition('a', vec![9]);

        q2.add_transition('b', vec![9]);

        q3.add_transition('b', vec![10]);

        q4.add_transition('b', vec![11]);

        q5.add_transition('a', vec![4]);
        q5.add_transition('b', vec![5]);
        q5.add_transition('c', vec![7, 8]);

        q6.add_transition('c', vec![9]);

        q7.add_transition('c', vec![12]);

        q8.add_transition('a', vec![5]);

        q9.add_transition('a', vec![1, 2, 3]);
        q9.add_transition('c', vec![6]);

        q10.add_transition('a', vec![13]);

        q11.add_transition('a', vec![14]);

        q12.add_transition('b', vec![5]);
        q12.add_transition('c', vec![7, 8]);

        q13.add_transition('a', vec![1, 2, 3, 4, 15]);
        q13.add_transition('b', vec![5, 16]);
        q13.add_transition('c', vec![6, 7, 8]);

        q14.add_transition('c', vec![17]);

        q15.add_transition('a', vec![10]);

        q16.add_transition('c', vec![18]);

        q17.add_transition('b', vec![5]);
        q17.add_transition('c', vec![8]);

        q18.add_transition('c', vec![13]);

        // Add states to automata in index order
        self.automata.add_state(q0);
        self.automata.add_state(q1);
        self.automata.add_state(q2);
        self.automata.add_state(q3);
        self.automata.add_state(q4);
        self.automata.add_state(q5);
        self.automata.add_state(q6);
        self.automata.add_state(q7);
        self.automata.add_state(q8);
        self.automata.add_state(q9);
        self.automata.add_state(q10);
        self.automata.add_state(q11);
        self.automata.add_state(q12);
        self.automata.add_state(q13);
        self.automata.add_state(q14);
        self.automata.add_state(q15);
        self.automata.add_state(q16);
        self.automata.add_state(q17);
        self.automata.add_state(q18);
    }

    fn can_recognize(&self, input: &str) -> bool {
        self.automata.can_recognize(input)
    }
}
