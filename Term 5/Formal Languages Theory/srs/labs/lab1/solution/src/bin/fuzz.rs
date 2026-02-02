use rand::prelude::*;
use solution::srs::{SRS, ShortLexString, Term};

fn fuzz_test<T: Term>(input: T, srs: &mut SRS<T>, srs_2: &mut SRS<T>) {
    let normal_forms_1 = srs.get_normal_forms(&input, 100).unwrap();

    println!("Normal forms from initial SRS: {:?}", normal_forms_1);
    println!("---");

    for nf in normal_forms_1 {
        let found = srs_2.search(&nf, &input, 12);
        println!("Checking normal form {:?} in second SRS: {:?}", nf, found);
        assert!(
            found,
            "Normal form {:?} from initial SRS not found in second SRS",
            nf
        );
    }
    println!("Fuzz test passed for input {:?}", input);
}

fn main() {
    const ABC: [&str; 3] = ["a", "b", "c"];
    const MAX_WORD_LENGTH: usize = 5; // 10 works but may be slow

    // Initial SRS
    let mut initial_srs = SRS::<ShortLexString>::new();
    initial_srs.add_rule("aabc", "bbaa");
    initial_srs.add_rule("b", "ccaa");
    initial_srs.add_rule("bc", "a");
    initial_srs.add_rule("aac", "");
    initial_srs.balance_all();
    initial_srs.sort();

    // New equivalent rules
    let mut equivalent_srs = SRS::<ShortLexString>::new();
    equivalent_srs.add_rule("c", "b");
    equivalent_srs.add_rule("ba", "ab");
    equivalent_srs.add_rule("bb", "a");
    equivalent_srs.add_rule("aaa", "b");
    equivalent_srs.add_rule("aab", "");

    equivalent_srs.balance_all();
    equivalent_srs.reverse_all(); // Reverse all rules
    equivalent_srs.sort();

    println!("Initial SRS: {:?}", initial_srs);
    println!("Equivalent SRS: {:?}", equivalent_srs);

    // Note: tests works fine, however it may exceed recursion limit because of epsilon rules
    fuzz_test(
        ShortLexString::new("aabc"),
        &mut initial_srs,
        &mut equivalent_srs,
    );

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
            "Fuzz test iteration {}: input {:?}",
            i + 1,
            random_input_str
        );
        fuzz_test(
            ShortLexString::new(random_input_str.as_str()),
            &mut initial_srs,
            &mut equivalent_srs,
        );
    }

    println!("Fuzz test completed");
}
