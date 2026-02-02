use crate::automata::{Automata, IAutomata, State};

pub struct DFA {
    pub automata: Automata,
}

impl IAutomata for DFA {
    fn new() -> Self {
        DFA {
            automata: Automata::new(),
        }
    }

    fn init_transitions(&mut self) {
        self.automata.states.clear();

        // Initial state is 6 (from DOT: dummy -> 6)
        self.automata.initial_state_index = 6;

        // Create states: State::new(name, index, is_final)
        let mut q0 = State::new("q0", 0, true);
        let mut q1 = State::new("q1", 1, false);
        let mut q2 = State::new("q2", 2, false);
        let mut q3 = State::new("q3", 3, true);
        let mut q4 = State::new("q4", 4, false);
        let mut q5 = State::new("q5", 5, true);
        let mut q6 = State::new("q6", 6, true);
        let mut q7 = State::new("q7", 7, false);
        let mut q8 = State::new("q8", 8, false);
        let mut q9 = State::new("q9", 9, false);
        let mut q10 = State::new("q10", 10, false);
        let mut q11 = State::new("q11", 11, false);
        let mut q12 = State::new("q12", 12, false);
        let mut q13 = State::new("q13", 13, true);
        let mut q14 = State::new("q14", 14, true);
        let mut q15 = State::new("q15", 15, false);
        let mut q16 = State::new("q16", 16, true);
        let mut q17 = State::new("q17", 17, false);
        let mut q18 = State::new("q18", 18, false);
        let mut q19 = State::new("q19", 19, false);
        let mut q20 = State::new("q20", 20, false);
        let mut q21 = State::new("q21", 21, false);
        let mut q22 = State::new("q22", 22, false);
        let mut q23 = State::new("q23", 23, true);
        let mut q24 = State::new("q24", 24, false);
        let mut q25 = State::new("q25", 25, false);
        let mut q26 = State::new("q26", 26, true);
        let mut q27 = State::new("q27", 27, false);
        let mut q28 = State::new("q28", 28, true);
        let mut q29 = State::new("q29", 29, false);
        let mut q30 = State::new("q30", 30, false);
        let mut q31 = State::new("q31", 31, true);
        let mut q32 = State::new("q32", 32, true);
        let mut q33 = State::new("q33", 33, false);

        // Add transitions from provided DOT

        // q0
        q0.add_transition('a', vec![17]);
        q0.add_transition('b', vec![0]);
        q0.add_transition('c', vec![29]);

        // q1
        q1.add_transition('a', vec![10]);
        q1.add_transition('c', vec![11]);

        // q2
        q2.add_transition('a', vec![0]);
        q2.add_transition('c', vec![3]);

        // q3
        q3.add_transition('a', vec![15]);
        q3.add_transition('b', vec![16]);
        q3.add_transition('c', vec![8]);

        // q4
        q4.add_transition('a', vec![5]);
        q4.add_transition('c', vec![11]);

        // q5
        q5.add_transition('a', vec![12]);
        q5.add_transition('b', vec![13]);
        q5.add_transition('c', vec![8]);

        // q6
        q6.add_transition('a', vec![7]);
        q6.add_transition('b', vec![0]);
        q6.add_transition('c', vec![8]);

        // q7
        q7.add_transition('a', vec![1]);
        q7.add_transition('b', vec![22]);

        // q8
        q8.add_transition('a', vec![0]);
        q8.add_transition('c', vec![9]);

        // q9
        q9.add_transition('a', vec![10]);
        q9.add_transition('b', vec![0]);
        q9.add_transition('c', vec![8]);

        // q10
        q10.add_transition('a', vec![1]);
        q10.add_transition('b', vec![4]);

        // q11
        q11.add_transition('c', vec![1]);

        // q12
        q12.add_transition('a', vec![33]);
        q12.add_transition('b', vec![22]);
        q12.add_transition('c', vec![11]);

        // q13
        q13.add_transition('a', vec![14]);
        q13.add_transition('b', vec![0]);
        q13.add_transition('c', vec![2]);

        // q14
        q14.add_transition('a', vec![12]);
        q14.add_transition('b', vec![31]);
        q14.add_transition('c', vec![8]);

        // q15
        q15.add_transition('a', vec![4]);
        q15.add_transition('b', vec![22]);

        // q16
        q16.add_transition('a', vec![17]);
        q16.add_transition('b', vec![0]);
        q16.add_transition('c', vec![2]);

        // q17
        q17.add_transition('b', vec![18]);

        // q18
        q18.add_transition('a', vec![19]);

        // q19
        q19.add_transition('c', vec![20]);

        // q20
        q20.add_transition('b', vec![0]);
        q20.add_transition('c', vec![21]);

        // q21
        q21.add_transition('a', vec![0]);

        // q22
        q22.add_transition('a', vec![23]);
        q22.add_transition('c', vec![11]);

        // q23
        q23.add_transition('a', vec![12]);
        q23.add_transition('b', vec![13]);
        q23.add_transition('c', vec![24]);

        // q24
        q24.add_transition('a', vec![0]);
        q24.add_transition('b', vec![0]);
        q24.add_transition('c', vec![25]);

        // q25
        q25.add_transition('a', vec![26]);
        q25.add_transition('b', vec![0]);
        q25.add_transition('c', vec![8]);

        // q26
        q26.add_transition('a', vec![27]);
        q26.add_transition('b', vec![28]);
        q26.add_transition('c', vec![29]);

        // q27
        q27.add_transition('a', vec![10]);
        q27.add_transition('b', vec![18]);
        q27.add_transition('c', vec![11]);

        // q28
        q28.add_transition('a', vec![14]);
        q28.add_transition('b', vec![0]);
        q28.add_transition('c', vec![8]);

        // q29
        q29.add_transition('a', vec![0]);
        q29.add_transition('c', vec![30]);

        // q30
        q30.add_transition('b', vec![0]);
        q30.add_transition('c', vec![29]);

        // q31
        q31.add_transition('a', vec![32]);
        q31.add_transition('b', vec![0]);
        q31.add_transition('c', vec![2]);

        // q32
        q32.add_transition('a', vec![12]);
        q32.add_transition('b', vec![31]);
        q32.add_transition('c', vec![24]);

        // q33
        q33.add_transition('a', vec![5]);
        q33.add_transition('b', vec![4]);
        q33.add_transition('c', vec![11]);

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
        self.automata.add_state(q19);
        self.automata.add_state(q20);
        self.automata.add_state(q21);
        self.automata.add_state(q22);
        self.automata.add_state(q23);
        self.automata.add_state(q24);
        self.automata.add_state(q25);
        self.automata.add_state(q26);
        self.automata.add_state(q27);
        self.automata.add_state(q28);
        self.automata.add_state(q29);
        self.automata.add_state(q30);
        self.automata.add_state(q31);
        self.automata.add_state(q32);
        self.automata.add_state(q33);
    }

    fn can_recognize(&self, input: &str) -> bool {
        self.automata.can_recognize(input)
    }
}
