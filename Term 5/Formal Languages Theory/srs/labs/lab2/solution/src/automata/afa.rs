use crate::automata::{Automata, IAutomata, State};

pub struct AFA {
    main: AFA_main,
    bcb: AFA_bcb,
    suf: AFA_suf,
}

impl IAutomata for AFA {
    fn new() -> Self {
        AFA {
            main: AFA_main::new(),
            bcb: AFA_bcb::new(),
            suf: AFA_suf::new(),
        }
    }

    fn init_transitions(&mut self) {
        self.main.init_transitions();
        self.bcb.init_transitions();
        self.suf.init_transitions();
    }

    fn can_recognize(&self, input: &str) -> bool {
        let main_accepts = self.main.can_recognize(input);
        let bcb_accepts = self.bcb.can_recognize(input);
        let suf_accepts = self.suf.can_recognize(input);

        main_accepts && bcb_accepts && suf_accepts
    }
}

/// Main (NFA A*B*) branch
pub struct AFA_main {
    pub automata: Automata,
}

impl IAutomata for AFA_main {
    fn new() -> Self {
        AFA_main {
            automata: Automata::new(),
        }
    }

    fn init_transitions(&mut self) {
        self.automata.states.clear();
        self.automata.initial_state_index = 0;

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

/// Invariant branch L1: controller that forbids substring "bcb"
pub struct AFA_bcb {
    pub automata: Automata,
}

impl IAutomata for AFA_bcb {
    fn new() -> Self {
        AFA_bcb {
            automata: Automata::new(),
        }
    }

    fn init_transitions(&mut self) {
        self.automata.states.clear();
        self.automata.initial_state_index = 0;

        // B0 (0), B1 (1), B2 (2) are accepting; Bdead (3) is non-accepting trap
        let mut b0 = State::new("B0", 0, true);
        let mut b1 = State::new("B1", 1, true);
        let mut b2 = State::new("B2", 2, true);
        let mut bdead = State::new("Bdead", 3, false);

        // B0
        b0.add_transition('b', vec![1]);
        b0.add_transition('a', vec![0]);
        b0.add_transition('c', vec![0]);

        // B1
        b1.add_transition('b', vec![1]);
        b1.add_transition('a', vec![0]);
        b1.add_transition('c', vec![2]);

        // B2
        b2.add_transition('b', vec![3]); // saw bcb -> trap
        b2.add_transition('a', vec![0]);
        b2.add_transition('c', vec![0]);

        // Bdead
        bdead.add_transition('a', vec![3]);
        bdead.add_transition('b', vec![3]);
        bdead.add_transition('c', vec![3]);

        self.automata.add_state(b0);
        self.automata.add_state(b1);
        self.automata.add_state(b2);
        self.automata.add_state(bdead);
    }

    fn can_recognize(&self, input: &str) -> bool {
        self.automata.can_recognize(input)
    }
}

/// Invariant branch L2: suffix controller (forbids final suffix "ac" or "bc")
pub struct AFA_suf {
    pub automata: Automata,
}

impl IAutomata for AFA_suf {
    fn new() -> Self {
        AFA_suf {
            automata: Automata::new(),
        }
    }

    fn init_transitions(&mut self) {
        self.automata.states.clear();
        self.automata.initial_state_index = 0;

        // S0 (0), Sa (1), Sb (2) are accepting; Sac (3), Sbc (4) are non-accepting
        let mut s0 = State::new("S0", 0, true);
        let mut sa = State::new("Sa", 1, true);
        let mut sb = State::new("Sb", 2, true);
        let mut sac = State::new("Sac", 3, false);
        let mut sbc = State::new("Sbc", 4, false);

        s0.add_transition('a', vec![1]);
        s0.add_transition('b', vec![2]);
        s0.add_transition('c', vec![0]);

        sa.add_transition('a', vec![1]);
        sa.add_transition('b', vec![2]);
        sa.add_transition('c', vec![3]);

        sb.add_transition('a', vec![1]);
        sb.add_transition('b', vec![2]);
        sb.add_transition('c', vec![4]);

        sac.add_transition('a', vec![1]);
        sac.add_transition('b', vec![2]);
        sac.add_transition('c', vec![0]);

        sbc.add_transition('a', vec![1]);
        sbc.add_transition('b', vec![2]);
        sbc.add_transition('c', vec![0]);

        self.automata.add_state(s0);
        self.automata.add_state(sa);
        self.automata.add_state(sb);
        self.automata.add_state(sac);
        self.automata.add_state(sbc);
    }

    fn can_recognize(&self, input: &str) -> bool {
        self.automata.can_recognize(input)
    }
}
