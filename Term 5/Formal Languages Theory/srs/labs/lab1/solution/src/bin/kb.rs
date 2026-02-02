use std::collections::HashSet;

use solution::srs::{Rule, SRS, ShortLexString, TString, Term};

/// Returns shortest common superstring of rule1.lhs and rule2.lhs
/// or None if they do not form a critical pair
fn get_scs_naive<T: Term>(rule1: &Rule<T>, rule2: &Rule<T>) -> Option<T> {
    // OPTIMIZATION: could cache results of this function
    // OPTIMIZATION: could use smarter algorithm for SCS like kmp or suffix arrays

    // Get shortest common superstring of rule1.lhs and rule2.lhs
    let lhs1 = rule1.get_ref().0;
    let lhs2 = rule2.get_ref().0;
    let len1 = lhs1.len();
    let len2 = lhs2.len();

    // Ensure to find the shortest one
    // OPTIMIZATION: could return immediately when found the first one
    let mut scs_shortest: Option<T> = None;

    println!("Finding SCS of {:?} and {:?}", rule1, rule2);
    // Check suffix of lhs1 with prefix of lhs2
    for i in 1..=len1.min(len2) {
        if &lhs1[len1 - i..] == &lhs2[..i] {
            scs_shortest = Some(T::new(&format!("{}{}", lhs1, &lhs2[i..])));
        }
    }

    if scs_shortest.is_some() {
        return scs_shortest;
    }

    // Check suffix of lhs2 with prefix of lhs1
    for i in 1..=len1.min(len2) {
        if &lhs2[len2 - i..] == &lhs1[..i] {
            scs_shortest = Some(T::new(&format!("{}{}", lhs2, &lhs1[i..])));
        }
    }
    return scs_shortest;
}

/// Returns shortest common superstring of rule1.lhs and rule2.lhs
/// or None if they do not form a critical pair
fn get_scs<T: Term>(rule1: &Rule<T>, rule2: &Rule<T>) -> Option<T> {
    // Compute length of longest suffix of `a` that is a prefix of `b`
    // using KMP prefix function on `b` and streaming `a` through it.
    fn overlap_suffix_prefix(a: &[u8], b: &[u8]) -> usize {
        if a.is_empty() || b.is_empty() {
            return 0;
        }

        // prefix function for pattern b
        let mut pi = vec![0usize; b.len()];
        for i in 1..b.len() {
            let mut j = pi[i - 1];
            while j > 0 && b[i] != b[j] {
                j = pi[j - 1];
            }
            if b[i] == b[j] {
                j += 1;
            }
            pi[i] = j;
        }

        // run KMP: feed text a against pattern b, keep the current match length j
        let mut j = 0usize;
        for &byte in a {
            while j > 0 && byte != b[j] {
                j = pi[j - 1];
            }
            if byte == b[j] {
                j += 1;
                if j == b.len() {
                    // full pattern matched; for our purpose that's the max possible overlap
                    break;
                }
            }
        }
        j
    }

    let lhs1 = rule1.get_ref().0;
    let lhs2 = rule2.get_ref().0;

    // Fast equality short-circuit
    if lhs1 == lhs2 {
        return Some(T::new(lhs1));
    }

    let a = lhs1.as_bytes();
    let b = lhs2.as_bytes();

    // overlap1: suffix of lhs1 matches prefix of lhs2
    let overlap1 = overlap_suffix_prefix(a, b);
    // overlap2: suffix of lhs2 matches prefix of lhs1
    let overlap2 = overlap_suffix_prefix(b, a);

    // Prefer overlap where lhs1 suffix matches lhs2 prefix if any (to match original behavior),
    // otherwise use the opposite direction; return None if no overlap.
    if overlap1 > 0 {
        let mut res = String::with_capacity(lhs1.len() + lhs2.len() - overlap1);
        res.push_str(lhs1);
        res.push_str(&lhs2[overlap1..]);
        return Some(T::new(&res));
    }
    if overlap2 > 0 {
        let mut res = String::with_capacity(lhs2.len() + lhs1.len() - overlap2);
        res.push_str(lhs2);
        res.push_str(&lhs1[overlap2..]);
        return Some(T::new(&res));
    }
    None
}

#[cfg(test)]
mod scs_tests {
    use super::*;
    fn assert_get_scs(r1: (&str, &str), r2: (&str, &str), expected: Option<TString>) {
        let rule1 = Rule::<TString>::new(r1.0, r1.1);
        let rule2 = Rule::<TString>::new(r2.0, r2.1);
        let result = get_scs(&rule1, &rule2);
        println!("Comparing {:?} and {:?} gives {:?}", rule1, rule2, result);
        assert_eq!(result, expected);
    }

    #[test]
    fn test_get_scs() {
        assert_get_scs(("a", "b"), ("a", "c"), Some(TString::new("a")));
        assert_get_scs(("a", "b"), ("b", "c"), None);
        assert_get_scs(("ab", "c"), ("bc", "d"), Some(TString::new("abc")));
        assert_get_scs(("abc", "d"), ("bcd", "e"), Some(TString::new("abcd")));
        assert_get_scs(("abc", "d"), ("cde", "e"), Some(TString::new("abcde")));
        assert_get_scs(("abc", "d"), ("xyz", "e"), None);
        assert_get_scs(("abab", "c"), ("baba", "d"), Some(TString::new("ababa")));
        assert_get_scs(("a", "c"), ("abcd", "d"), Some(TString::new("abcd")));
        assert_get_scs(("abab", "c"), ("abab", "d"), Some(TString::new("abab")));
        assert_get_scs(("ab", "c"), ("abab", "d"), Some(TString::new("abab")));
        assert_get_scs(("abab", "c"), ("ab", "d"), Some(TString::new("abab")));
        assert_get_scs(("ab", "c"), ("bab", "d"), Some(TString::new("abab")));
        assert_get_scs(("bab", "c"), ("ab", "d"), Some(TString::new("bab")));
    }
}

/// Returns critical pair formed by rule with itself
/// Asserts that critical pair has size 1 or 2
fn get_own_critical_pair<T: Term>(rule: &Rule<T>) -> HashSet<T> {
    let lhs = rule.get_ref().0;
    let len = lhs.len();

    if len < 2 {
        return HashSet::new(); // No borders possible
    }

    let mut scs: Option<T> = None;
    // Check for non-empty borders
    for i in 1..(len / 2 + 1) {
        // if prefix == suffix
        if &lhs[..i] == &lhs[len - i..] {
            scs = Some(T::new(&format!("{}{}", &lhs, &lhs[len - i..])));
            break;
        }
    }
    if scs.is_none() {
        return HashSet::new(); // No borders found
    }

    // Return critical pair
    let scs = scs.unwrap();
    println!("SCS of {:?} with itself is {:?}", rule, scs);
    let result = rule.apply(&scs);
    assert!(result.len() < 3);
    assert!(result.len() > 0);
    return result;
}

#[cfg(test)]
mod own_tests {
    use super::*;

    #[test]
    fn test_get_own_critical_pairs() {
        let rule = Rule::<TString>::new("aaa", "b");
        let pair = get_own_critical_pair(&rule);
        assert_eq!(pair.len(), 2);
        assert!(pair.contains(&TString::new("ba")));
        assert!(pair.contains(&TString::new("ab")));
    }
}

fn complete_rules_with_itself<T: Term>(s: &mut SRS<T>) -> usize {
    // Say we have rules l1 -> r1 : aa -> b
    // It forms a critical pair with itself in "aaa" -> "ba" and "aaa" -> "ab"
    // So we result in pair like ("ba", "ab")
    // And need to add rule "ba" -> "ab" or "ab" -> "ba" depending on order
    // This will be enough for confluence:
    // aa -> b    aaaa -> aba || bb
    // aa -> b    aaa -> ab || ba => new_rule ba -> ab => aba -> aab -> bb

    // Single pass to add all new rules
    let mut new_rules: Vec<Rule<T>> = vec![];
    for rule in &s.rules {
        // Get critical pair with itself like ("ba", "ab") with "aa" -> "b"
        let critical_pair = get_own_critical_pair(rule);

        // Find normal forms of overlapping word
        // REFACTOR: can get normal forms directly from own srs
        let mut normal_forms: HashSet<T> = HashSet::new();
        for t in &critical_pair {
            normal_forms.extend(s.get_normal_forms(t, 100).unwrap());
        }
        assert!(normal_forms.len() < 3);

        if normal_forms.len() == 2 {
            let mut iter = normal_forms.iter();
            let t1 = iter.next().unwrap().as_str();
            let t2 = iter.next().unwrap().as_str();
            let mut self_fix_rule = Rule::<T>::new(t1, t2);
            self_fix_rule.balance();
            let (t1_balanced, t2_balanced) = self_fix_rule.get_ref();
            println!(
                "Adding new balanced rule {:?} -> {:?} to resolve self-critical pair in {:?}",
                t1_balanced, t2_balanced, rule
            );
            new_rules.push(Rule::new(t1_balanced, t2_balanced));
        }
    }

    // Update SRS with new rules
    let new_rules_len = new_rules.len();
    for rule in new_rules {
        let (lhs, rhs) = rule.get_ref();
        // add_rule_and_check::<T>(s, lhs, rhs);
        s.add_rule(lhs, rhs);
    }
    return new_rules_len;
}

fn complete_rules_with_others<T: Term>(s: &mut SRS<T>) -> usize {
    // Say we have rules l1 -> r1 : aa -> b and l2 -> r2 : ab -> c
    // It forms a critical pair in "aab" -> "bc" and "aab" -> "ca"
    // So we result in pair like ("bc", "ca")
    // And need to add rule "bc" -> "ca" or "ca" -> "bc" depending on order
    // This will be enough for confluence:
    // aa -> b    aab -> bc || ca
    // ab -> c    aab -> ca || bc => new_rule bc -> ca => abc -> ac || ba

    let mut new_rules: HashSet<Rule<T>> = HashSet::new();

    // Compare each rule with every other rule
    // Collect problematic words formed by their overlaps
    for i in 0..s.rules.len() - 1 {
        for j in i + 1..s.rules.len() {
            let rule1 = &s.rules[i];
            let rule2 = &s.rules[j];
            if let Some(scs) = get_scs(rule1, rule2) {
                println!("SCS of {:?} and {:?} is {:?}", rule1, rule2, scs);

                // Find normal forms of overlapping word
                let rule_applied: HashSet<T> = s.get_normal_forms(&scs, 100).unwrap();
                println!(
                    "Normal forms of {:?} with SRS {:?} are {:?}",
                    scs, s, rule_applied
                );
                assert_ne!(
                    rule_applied.len(),
                    0,
                    "No normal forms for {:?} with SRS {:?}",
                    scs,
                    s
                );
                if rule_applied.len() == 1 {
                    continue; // No conflict
                }

                // Sort all normal forms and add rules between them
                let mut forms_vec: Vec<T> = rule_applied.into_iter().collect();
                forms_vec.sort();
                for i in (1..forms_vec.len()).rev() {
                    println!(
                        "Adding new balanced rule {:?} -> {:?} to resolve critical pair in {:?}",
                        forms_vec[i].as_str(),
                        forms_vec[i - 1].as_str(),
                        scs
                    );
                    new_rules.insert(Rule::new(forms_vec[i].as_str(), forms_vec[i - 1].as_str()));
                }
            }
        }
    }

    // Update SRS with new rules
    let new_rules_len = new_rules.len();
    for rule in new_rules {
        let (lhs, rhs) = rule.get_ref();
        // add_rule_and_check::<T>(s, lhs, rhs);
        s.add_rule(lhs, rhs);
    }

    return new_rules_len;
}

#[cfg(test)]
mod complete_tests {
    use super::*;

    #[test]
    fn test_complete_rules_with_others() {
        let mut s = SRS::<TString>::new();
        s.add_rule("ab", "b");
        s.add_rule("bd", "c");
        s.balance_all();
        s.sort();

        let new_rules_count = complete_rules_with_others(&mut s);
        assert_eq!(new_rules_count, 1);
        assert!(s.rules.contains(&Rule::new("ac", "c")));
        println!("SRS after completing with others: {:?}", s);
    }

    #[test]
    fn test_complete_self() {
        let mut s = SRS::<TString>::new();
        s.add_rule("aa", "b");

        complete_rules_with_itself(&mut s);
        assert!(s.rules.contains(&Rule::new("ab", "ba")));
        println!("SRS after self-completion: {:?}", s);
    }

    #[test]
    fn test_complete_default() {}
}

fn knuth_bendix<T: Term>(s: &SRS<T>) -> SRS<T> {
    let mut new_s = s.clone();

    let mut total_new_rules = 0;
    let mut rules_added = 1;
    while rules_added > 0 {
        rules_added = 0;
        rules_added += complete_rules_with_itself(&mut new_s);
        rules_added += complete_rules_with_others(&mut new_s);
        total_new_rules += rules_added;
    }

    println!("Total new rules added in KB: {}", total_new_rules);
    new_s
}

#[cfg(test)]
mod kb_tests {
    use super::*;

    #[test]
    fn test_kb() {
        let mut s = SRS::<TString>::new();
        s.add_rule("bb", "a");
        s.add_rule("c", "b");
        s.balance_all();
        s.sort();
        println!("Initial SRS: {:?}", s);

        let mut new_s = knuth_bendix(&s);
        println!("New SRS after KB: {:?}", new_s);
        new_s.sort();

        s.add_rule("ab", "ba");
        s.sort();
        assert_eq!(new_s.rules, s.rules);
    }

    #[test]
    fn test_kb_only_self_completion() {
        let mut s = SRS::<TString>::new();
        s.add_rule("bb", "a");

        let new_s = knuth_bendix(&s);
        println!("New SRS after KB: {:?}", new_s);
        assert!(new_s.rules.contains(&Rule::new("ab", "ba")));
    }
}

fn main() {
    let mut s = SRS::<ShortLexString>::new();

    // Add my 22nd version of SRS
    s.add_rule("bbaa", "aabc");
    s.add_rule("ccaa", "b");
    s.add_rule("bc", "a");
    s.add_rule("aac", "");

    // sort
    s.balance_all();
    s.sort();
    println!("Initial SRS: {:?}", s);

    let mut new_s = knuth_bendix(&s);
    new_s.sort();
    println!("Completed SRS: {:?}", new_s);
}
