use core::{fmt, panic, str};
use std::collections::{HashMap, HashSet, VecDeque};
use std::fmt::Debug;
use std::{
    cmp::{Ordering, min},
    hash::Hash,
};

pub trait Term: Ord + Clone + Hash + Debug {
    fn is_empty(&self) -> bool;
    fn new(value: &str) -> Self;
    fn as_str(&self) -> &str;
}

#[derive(Clone, PartialEq, Eq, Hash)]
pub struct TString {
    value: String,
}

impl Term for TString {
    fn new(value: &str) -> Self {
        let mut value_updated = value.to_string();
        // Retain only lowercase ASCII characters
        value_updated.retain(|c| c.is_ascii_lowercase());
        if value_updated.len() != value.len() {
            println!(
                "Warning: Non-lowercase ASCII characters were removed from '{}', resulting in '{}'",
                value, value_updated
            );
        }

        // Treat "ε" as an empty string
        if value_updated == "ε" {
            value_updated.clear();
        }

        Self {
            value: value_updated,
        }
    }

    fn is_empty(&self) -> bool {
        self.value.is_empty()
    }

    fn as_str(&self) -> &str {
        &self.value
    }
}

impl PartialOrd for TString {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        // Return equal if both strings are equal
        if self.value == other.value {
            return Some(Ordering::Equal);
        }

        // Return empty string as the smallest one
        if self.is_empty() && !other.is_empty() {
            return Some(Ordering::Less);
        }
        if !self.is_empty() && other.is_empty() {
            return Some(Ordering::Greater);
        }

        let min_len = min(self.value.len(), other.value.len());

        // Get byte slices for comparison, bc rust String cannot be indexed directly
        let self_bytes = self.value.as_bytes();
        let other_bytes = other.value.as_bytes();

        // Compare characters from the end of the strings
        // Return the ordering of the first different character found
        let mut i = 1;
        while i <= min_len {
            if self_bytes[self.value.len() - i] != other_bytes[other.value.len() - i] {
                // Compare ASCII chars
                return Some(
                    self_bytes[self.value.len() - i].cmp(&other_bytes[other.value.len() - i]),
                );
            }
            i += 1;
        }

        // If all characters are the same up to the length of the shorter string,
        // the shorter string is considered smaller
        Some(self.value.len().cmp(&other.value.len()))
    }
}

impl Ord for TString {
    fn cmp(&self, other: &Self) -> Ordering {
        self.partial_cmp(other).unwrap()
    }
}

impl fmt::Debug for TString {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if self.value.is_empty() {
            write!(f, "ε")
        } else {
            write!(f, "{}", self.value)
        }
    }
}

// ShortLexString: same as TString, but ordering is ShortLex (shorter first, then lex)
// TODO: avoid code duplication with TString
#[derive(Clone, PartialEq, Eq, Hash)]
pub struct ShortLexString {
    value: String,
}

impl Term for ShortLexString {
    fn new(value: &str) -> Self {
        let mut value_updated = value.to_string();
        value_updated.retain(|c| c.is_ascii_lowercase());
        if value_updated.len() != value.len() {
            println!(
                "Warning: Non-lowercase ASCII characters were removed from '{}', resulting in '{}'",
                value, value_updated
            );
        }
        if value_updated == "ε" {
            value_updated.clear();
        }
        Self {
            value: value_updated,
        }
    }

    fn is_empty(&self) -> bool {
        self.value.is_empty()
    }

    fn as_str(&self) -> &str {
        &self.value
    }
}

impl PartialOrd for ShortLexString {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        // ShortLex: shorter string is less, if equal length, compare lexicographically
        match self.value.len().cmp(&other.value.len()) {
            Ordering::Equal => Some(self.value.cmp(&other.value)),
            ord => Some(ord),
        }
    }
}

impl Ord for ShortLexString {
    fn cmp(&self, other: &Self) -> Ordering {
        self.partial_cmp(other).unwrap()
    }
}

impl fmt::Debug for ShortLexString {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if self.value.is_empty() {
            write!(f, "ε")
        } else {
            write!(f, "{}", self.value)
        }
    }
}

#[cfg(test)]
mod tstring_tests {
    use super::*;

    fn test_cmp(s1: &str, s2: &str, expected: Ordering) {
        let t1 = TString::new(s1);
        let t2 = TString::new(s2);
        assert_eq!(t1.cmp(&t2), expected);
    }

    #[test]
    fn test_cmp_cases() {
        test_cmp("abc", "abc", Ordering::Equal);
        test_cmp("", "abc", Ordering::Less);
        test_cmp("abc", "", Ordering::Greater);
        test_cmp("abc", "abd", Ordering::Less);
        test_cmp("abd", "abc", Ordering::Greater);
        test_cmp("abc", "ab", Ordering::Greater);
        test_cmp("ab", "abc", Ordering::Less);
        test_cmp("bc", "abc", Ordering::Less);
        test_cmp("a", "b", Ordering::Less);
        test_cmp("b", "a", Ordering::Greater);
        test_cmp("", "", Ordering::Equal);
    }
}

#[derive(Clone, Hash)]
pub struct Rule<T: Term> {
    lhs: T,
    rhs: T,
}

impl<T: Term> Rule<T> {
    pub fn new(lhs: &str, rhs: &str) -> Self {
        Self {
            lhs: T::new(lhs),
            rhs: T::new(rhs),
        }
    }

    /// Swaps lhs and rhs of the rule ensuring that lhs >= rhs
    pub fn balance(&mut self) {
        if self.lhs < self.rhs {
            std::mem::swap(&mut self.lhs, &mut self.rhs);
        }
    }

    pub fn reverse(&mut self) {
        std::mem::swap(&mut self.lhs, &mut self.rhs);
    }

    pub fn get_ref(&self) -> (&str, &str) {
        (&self.lhs.as_str(), &self.rhs.as_str())
    }

    pub fn executes_on(&self, s: &T) -> bool {
        s.as_str().contains(&self.lhs.as_str())
    }

    /// Find all substrings
    fn get_substring_indices_naive(s: &str, sub: &str) -> Vec<usize> {
        // OPTIMIZATION: could be done with Knuth-Morris-Pratt algorithm

        let mut indices = Vec::new();
        let mut pos = 0;
        while let Some(idx) = s[pos..].find(sub) {
            indices.push(pos + idx);
            pos += idx + 1; // Move forward by 1 to allow overlap
            if pos > s.len() - sub.len() {
                break;
            }
        }
        indices
    }

    fn get_substring_indices(s: &str, pat: &str) -> Vec<usize> {
        if pat.is_empty() {
            return (0..=s.len()).collect();
        }

        // OPTIMIZATION: Use crates like ('twoway' is deprecated) 'memchr'
        let s_bytes = s.as_bytes();
        let pat_bytes = pat.as_bytes();
        let mut lps: Vec<usize> = vec![0; pat_bytes.len()];
        // Build LPS array
        let mut len = 0;
        for i in 1..pat_bytes.len() {
            while len > 0 && pat_bytes[i] != pat_bytes[len] {
                len = lps[len - 1];
            }
            if pat_bytes[i] == pat_bytes[len] {
                len += 1;
                lps[i] = len;
            }
        }
        // Search
        let mut res = Vec::new();
        let mut i = 0;
        let mut j = 0;
        while i < s_bytes.len() {
            if s_bytes[i] == pat_bytes[j] {
                i += 1;
                j += 1;
            }
            if j == pat_bytes.len() {
                res.push(i - j);
                j = lps[j - 1];
            } else if i < s_bytes.len() && s_bytes[i] != pat_bytes[j] {
                if j != 0 {
                    j = lps[j - 1];
                } else {
                    i += 1;
                }
            }
        }
        res
    }

    /// Returns a set of all possible results after applying the rule
    pub fn apply(&self, s: &T) -> HashSet<T> {
        let mut results = HashSet::new();

        let s_str = s.as_str();
        let lhs_str = self.lhs.as_str();
        let rhs_str = self.rhs.as_str();
        let lhs_len = lhs_str.len();
        let rhs_len = rhs_str.len();

        // Collect indices first so we can reserve and avoid repeated work
        let indices = Self::get_substring_indices(s_str, lhs_str);
        results.reserve(indices.len());

        for index in indices {
            // pre-allocate exact capacity to avoid extra reallocs
            let mut new_value =
                String::with_capacity(s_str.len().saturating_sub(lhs_len) + rhs_len);
            new_value.push_str(&s_str[..index]);
            new_value.push_str(rhs_str);
            new_value.push_str(&s_str[index + lhs_len..]);
            results.insert(T::new(&new_value));
            println!(
                "Applying rule {:?} -> {:?} on {:?} with result {:?}",
                self.lhs, self.rhs, s, results
            );
        }
        results
    }
}

// Compare first by lhs, then by rhs if lhs are equal
impl<T: Term> PartialOrd for Rule<T> {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        match self.lhs.partial_cmp(&other.lhs) {
            Some(Ordering::Equal) => self.rhs.partial_cmp(&other.rhs),
            ord => ord,
        }
    }
}

impl<T: Term> Ord for Rule<T> {
    fn cmp(&self, other: &Self) -> Ordering {
        self.partial_cmp(other).unwrap()
    }
}

impl<T: Term> fmt::Debug for Rule<T> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:?} -> {:?}", self.lhs.as_str(), self.rhs.as_str())
    }
}

impl<T: Term> PartialEq for Rule<T> {
    fn eq(&self, other: &Self) -> bool {
        self.lhs == other.lhs
    }
}

impl<T: Term> Eq for Rule<T> {}

#[cfg(test)]
mod rule_tests {
    use super::*;

    fn assert_apply(lhs: &str, rhs: &str, input: &str, expected: Vec<&str>) {
        let rule = Rule::<TString>::new(lhs, rhs);
        let input_t = TString::new(input);
        let results = rule.apply(&input_t);
        let expected_t: HashSet<TString> = expected.iter().map(|&s| TString::new(s)).collect();
        println!(
            "Applying rule {:?} -> {:?} on {:?} gives {:?}",
            rule.lhs, rule.rhs, input_t, results
        );
        assert_eq!(results, expected_t);
    }

    #[test]
    fn test_apply_overlap_cases() {
        // Overlapping words
        assert_apply("aa", "b", "aaa", vec!["ba", "ab"]);
        assert_apply("aaa", "b", "aaaa", vec!["ba", "ab"]);

        // One occurrence
        assert_apply("aa", "b", "aa", vec!["b"]);

        // No occurrence
        assert_apply("aa", "b", "ab", vec![]);
    }

    #[test]
    fn test_rule_apply() {
        assert_apply("ab", "c", "ababab", vec!["cabab", "abcab", "ababc"]);
        assert_apply("a", "", "aaa", vec!["aa"]);
        assert_apply("a", "", "bbb", vec![]);
    }

    fn assert_cmp(r1: (&str, &str), r2: (&str, &str), expected: Ordering) {
        let rule1 = Rule::<TString>::new(r1.0, r1.1);
        let rule2 = Rule::<TString>::new(r2.0, r2.1);
        assert_eq!(rule1.cmp(&rule2), expected);
    }

    #[test]
    fn test_rule_cmp() {
        assert_cmp(("a", "b"), ("a", "c"), Ordering::Less);
        assert_cmp(("a", "b"), ("a", "b"), Ordering::Equal);
        assert_cmp(("a", "b"), ("a", "a"), Ordering::Greater);
        assert_cmp(("b", "a"), ("a", "a"), Ordering::Greater);
        assert_cmp(("aabc", "bbaa"), ("b", "aaa"), Ordering::Greater);
        assert_cmp(("aabc", "bbaa"), ("aacc", "aaa"), Ordering::Less);
    }
}

#[derive(Clone, Debug)]
pub struct SRS<T: Term> {
    pub rules: Vec<Rule<T>>,
    get_normal_forms_cache: HashMap<T, HashSet<T>>,
    rules_to_empty: HashSet<T>,
}

impl<T: Term> SRS<T> {
    pub fn new() -> Self {
        Self {
            rules: Vec::new(),
            get_normal_forms_cache: HashMap::new(),
            rules_to_empty: HashSet::new(),
        }
    }

    /// Checks if the rule is already in SRS
    pub fn has(&self, rule: &Rule<T>) -> bool {
        self.rules.contains(rule)
    }

    /// Reverses all rules in the SRS
    pub fn reverse_all(&mut self) {
        for rule in &mut self.rules {
            rule.reverse();
        }
    }

    /// Adds a new rule to the SRS.
    pub fn add_rule(&mut self, first: &str, second: &str) {
        let rule = Rule::new(first, second);
        println!(
            "Added rule: {:?} -> {:?}",
            rule.get_ref().0,
            rule.get_ref().1
        );

        // Ensure no duplicate rules
        assert!(
            !self.has(&rule),
            "Rule {} -> {} already exists in SRS ({:?})",
            first,
            second,
            rule
        );
        self.rules.push(rule.clone());

        // Remember rules that lead to empty string
        if rule.rhs.is_empty() {
            self.rules_to_empty.insert(rule.lhs.clone());
        }

        self.sort();
        println!("Current SRS rules: {:?}", self.rules);
    }

    /// Sorts the rules in the SRS by lhs, then by rhs
    pub fn sort(&mut self) {
        self.rules.sort();
    }

    /// Ensures the rule is in the correct order (lhs >= rhs)
    pub fn balance_all(&mut self) {
        for rule in &mut self.rules {
            rule.balance();
        }
    }

    /// Applies all rules to the string ONCE and returns the resulting set
    fn process(&self, s: &T) -> HashSet<T> {
        let mut processed = HashSet::<T>::new();

        // aac -> ε seems to cause no issues with KB
        // // Replace all lhs that lead to empty string
        // let emptied_s: T = {
        //     let mut temp = s.as_str().to_string();
        //     for lhs in &self.rules_to_empty {
        //         temp = temp.replace(lhs.as_str(), "");
        //     }
        //     T::new(&temp)
        // };

        // Apply all rules to the emptied string and save the results
        for rule in &self.rules {
            processed.extend(rule.apply(&s));
        }
        processed
    }

    /// Process the SRS from start to s using BFS up to max_term_len
    pub fn search(&self, start: &T, s: &T, max_term_len: usize) -> bool {
        let goal = s.clone();
        let mut queue = VecDeque::<T>::new();
        let mut visited = HashSet::<T>::new();
        queue.push_back(start.clone());
        while let Some(current) = queue.pop_front() {
            // Skip too long terms
            if current.as_str().len() > max_term_len {
                continue;
            }

            if visited.contains(&current) {
                continue;
            }

            if current == goal {
                return true;
            }

            visited.insert(current.clone());

            let processed = self.process(&current);
            for p in processed {
                if !visited.contains(&p) {
                    queue.push_back(p);
                }
            }
        }
        false
    }

    /// Returns a set of all normal forms reachable from the string s
    /// If tree gets too large, returns Err with the normal forms found so far
    pub fn get_normal_forms(&self, s: &T, max_term_len: usize) -> Result<HashSet<T>, HashSet<T>> {
        println!("Getting normal forms for string: {:?}", s);
        // Strings that cannot be processed further
        let mut normal_forms = HashSet::<T>::new();

        // Use Vec for iteration stack
        let mut pending = Vec::<T>::new();
        // HashSet for O(1) membership checks
        let mut pending_set = HashSet::<T>::new();
        pending.push(s.clone());
        pending_set.insert(s.clone());

        let mut visited = HashSet::<T>::new();

        // Process pending until no new strings are generated
        while let Some(current) = pending.pop() {
            // Safety guard against explosive growth
            if pending_set.len() > 1000 {
                return Err(normal_forms);
            }

            // Skip too long terms
            if current.as_str().len() > max_term_len {
                continue;
            }

            println!("GetNormalForms: Processing strings: {:?}", pending_set);
            println!("GetNormalForms: Current string: {:?}", current);
            println!("GetNormalForms: Normal forms so far: {:?}", normal_forms);

            // Remove from membership set since we're processing it now
            pending_set.remove(&current);
            // Avoid re-processing the same string
            if visited.contains(&current) {
                continue;
            }
            visited.insert(current.clone());

            let processed = self.process(&current);
            if processed.is_empty() {
                // No rules could be applied, this is a normal form
                if !normal_forms.contains(&current) {
                    normal_forms.insert(current);
                }
            } else {
                // Add all newly processed strings to the pending stack if not seen
                for p in processed {
                    if !pending_set.contains(&p) && !normal_forms.contains(&p) {
                        pending.push(p.clone());
                        pending_set.insert(p);
                    }
                }
            }
        }
        return Ok(normal_forms);
    }

    pub fn clear_cache(&mut self) {
        self.get_normal_forms_cache.clear();
    }
}

#[cfg(test)]
mod srs_tests {
    use super::*;

    #[test]
    fn test_has() {
        let mut srs = SRS::<TString>::new();
        srs.add_rule("a", "b");
        srs.add_rule("b", "c");

        // Treat "a" -> "b" and "a" -> "c" as equal rules
        assert!(srs.has(&Rule::new("a", "b")));
        assert!(srs.has(&Rule::new("a", "c")));
        assert!(srs.has(&Rule::new("b", "a")));
        assert!(!srs.has(&Rule::new("c", "a")));
    }

    fn assert_process(srs: &SRS<TString>, input: &str, expected: Vec<&str>) {
        let input_t = TString::new(input);
        let processed = srs.process(&input_t);
        let expected_t: HashSet<TString> = expected.iter().map(|&s| TString::new(s)).collect();
        assert_eq!(processed, expected_t);
    }

    #[test]
    fn test_srs_process() {
        let mut srs = SRS::<TString>::new();
        srs.add_rule("b", "a");
        srs.add_rule("c", "b");

        assert_process(&srs, "bab", vec!["aab", "baa"]);
    }

    fn assert_get_normal_forms(srs: &mut SRS<TString>, input: &str, expected: Vec<&str>) {
        let input_t = TString::new(input);
        let normal_forms = srs.get_normal_forms(&input_t, 100).unwrap();
        let expected_t: HashSet<TString> = expected.iter().map(|&s| TString::new(s)).collect();
        assert_eq!(normal_forms, expected_t);
    }

    #[test]
    fn test_srs_get_normal_forms_easy() {
        let mut srs = SRS::<TString>::new();
        srs.add_rule("ab", "d");
        srs.add_rule("abc", "e");

        assert_get_normal_forms(&mut srs, "a", vec!["a"]);
        assert_get_normal_forms(&mut srs, "abc", vec!["dc", "e"]);
    }

    #[test]
    fn test_srs_get_normal_forms_complex() {
        let mut srs = SRS::<TString>::new();
        // Add my 22nd version of SRS
        srs.add_rule("aabc", "bbaa");
        srs.add_rule("b", "ccaa");
        srs.add_rule("bc", "a");
        srs.add_rule("aac", "");

        // Empty test
        assert_get_normal_forms(&mut srs, "a", vec!["a"]);
        // Readme test 1
        assert_get_normal_forms(&mut srs, "aabc", vec!["cccaaaa", "acaaaa", "aaa", "c"]);
        // Readme test 2
        assert_get_normal_forms(&mut srs, "bc", vec!["a", "cc"]);
    }
}
