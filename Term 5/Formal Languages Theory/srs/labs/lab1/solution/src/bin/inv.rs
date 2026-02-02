use rand::prelude::*;
use solution::srs::{SRS, ShortLexString, Term};

// Note: See README.md for definitions of invariants

fn calc_inv1<T: Term>(t: &T) -> u8 {
    let count_a = t.as_str().chars().filter(|&c| c == 'a').count();
    let count_b = t.as_str().chars().filter(|&c| c == 'b').count();
    let count_c = t.as_str().chars().filter(|&c| c == 'c').count();
    let inv1 = (2 * count_a + count_b + count_c) % 5;
    println!("Calculating inv1 for {:?}: {}", t, inv1);
    inv1 as u8
}

fn assert_inv1_equivalence<T: Term>(srs1: &SRS<T>, srs2: &SRS<T>, word: &T) {
    let word_inv1 = calc_inv1(word);
    let normal_form_initial = srs1.get_normal_forms(word, 100).unwrap();

    // Check all normal forms to be consistent with initial word
    for form in normal_form_initial {
        let inv1 = calc_inv1(&form);
        assert!(inv1 == word_inv1);
    }

    // Check all normal forms to be consistent with equivalent SRS for completed SRS
    let normal_form_equivalent = srs2.get_normal_forms(word, 100).unwrap();
    assert!(normal_form_equivalent.len() == 1); // Ensure confluence
    let form = normal_form_equivalent.iter().next().unwrap();
    let inv1 = calc_inv1(form);
    assert!(inv1 == word_inv1);
}

fn calc_inv2<T: Term>(t: &T) -> bool {
    let count_ccc = t.as_str().matches("ccc").count();
    let inv2 = count_ccc == 0;
    println!("Calculating inv2 for {:?}: {}", t, count_ccc);
    inv2
}

fn assert_inv2_equivalence<T: Term>(srs1: &SRS<T>, srs2: &SRS<T>, word: &T) {
    let word_inv2 = calc_inv2(word);

    // If the word already violates inv2, no need to check further
    if !word_inv2 {
        println!("Word {:?} violates inv2, skipping further checks.", word);
        return;
    }

    let normal_form_initial = srs1.get_normal_forms(word, 100).unwrap();

    // Check all normal forms to be consistent with initial word
    for form in normal_form_initial {
        let inv2 = calc_inv2(&form);
        assert!(inv2 == word_inv2);
    }

    // Check all normal forms to be consistent with equivalent SRS for completed SRS
    let normal_form_equivalent = srs2.get_normal_forms(word, 100).unwrap();
    assert!(normal_form_equivalent.len() == 1); // Ensure confluence
    let form = normal_form_equivalent.iter().next().unwrap();
    let inv2 = calc_inv2(form);
    assert!(inv2 == word_inv2);
}

fn calc_inv3<T: Term>(t: &T) -> bool {
    let mut level = 0;
    let mut max_level = 0;
    for c in t.as_str().chars() {
        match c {
            'a' => level += 1,
            'b' => level += 2,
            'c' => level -= 1,
            _ => {}
        }
        max_level = max_level.max(level);
    }
    let result = max_level <= 3;
    println!("Calculating inv3 for {:?}: {}", t, result);
    result
}

fn assert_inv3_equivalence<T: Term>(srs1: &SRS<T>, srs2: &SRS<T>, word: &T) {
    let word_inv3 = calc_inv3(word);

    if word_inv3 == false {
        println!("Word {:?} violates inv3, skipping further checks.", word);
        return;
    }

    let normal_form_initial = srs1.get_normal_forms(word, 100).unwrap();

    // Check all normal forms to be consistent with initial word
    for form in normal_form_initial {
        let inv3 = calc_inv3(&form);
        assert!(inv3 == word_inv3);
    }

    // Check all normal forms to be consistent with equivalent SRS for completed SRS
    let normal_form_equivalent = srs2.get_normal_forms(word, 100).unwrap();
    assert!(normal_form_equivalent.len() == 1); // Ensure confluence
    let form = normal_form_equivalent.iter().next().unwrap();
    let inv3 = calc_inv3(form);
    assert!(inv3 == word_inv3);
}

fn main() {
    const ABC: [&str; 3] = ["a", "b", "c"];
    const MAX_WORD_LENGTH: usize = 10;

    // Initial SRS
    let mut initial_srs = SRS::<ShortLexString>::new();
    initial_srs.add_rule("aabc", "bbaa");
    initial_srs.add_rule("b", "ccaa");
    initial_srs.add_rule("bc", "a");
    initial_srs.add_rule("aac", "");
    initial_srs.balance_all();
    initial_srs.sort();

    // Completed SRS
    let mut equivalent_srs = SRS::<ShortLexString>::new();
    equivalent_srs.add_rule("c", "b");
    equivalent_srs.add_rule("ba", "ab");
    equivalent_srs.add_rule("bb", "a");
    equivalent_srs.add_rule("aaa", "b");
    equivalent_srs.add_rule("aab", "");
    equivalent_srs.balance_all();
    equivalent_srs.sort();

    assert_inv1_equivalence(&initial_srs, &equivalent_srs, &ShortLexString::new("abac"));

    let mut rng = rand::rng();
    for i in 0..10 {
        let random_length = rng.random_range(1..MAX_WORD_LENGTH + 1);
        let random_input_str: String = (0..random_length)
            .map(|_| {
                let idx = rng.random_range(0..ABC.len());
                ABC[idx]
            })
            .collect();
        println!(
            "Invariant test iteration {}: input {:?}",
            i + 1,
            random_input_str
        );
        println!("--- Inv1 ---");
        assert_inv1_equivalence(
            &initial_srs,
            &equivalent_srs,
            &ShortLexString::new(random_input_str.as_str()),
        );
        println!("--- Inv2 ---");
        assert_inv2_equivalence(
            &initial_srs,
            &equivalent_srs,
            &ShortLexString::new(random_input_str.as_str()),
        );
        println!("--- Inv3 ---");
        assert_inv3_equivalence(
            &initial_srs,
            &equivalent_srs,
            &ShortLexString::new(random_input_str.as_str()),
        );
        println!("---");
    }

    println!("All invariant equivalence tests passed");
}
