package task1;

import java.util.Iterator;
import java.util.Objects;

public class SuffixList implements Iterable<Integer> {
    private StringBuilder s;
    private String w;

    public void setW(String s){
        this.w = s;
    }
    public SuffixList ( StringBuilder s , String w) {
        this.s = s;
        this.w = w;
    }
    public Iterator<Integer> iterator() { return new SuffixIterator(); }
    private class SuffixIterator implements Iterator<Integer> {
        private int pos;

        private Integer GetNext(){
            int tpos = pos + 1;
            while (tpos <= s.length() - w.length()){
                if (Objects.equals(s.substring(tpos, tpos + w.length()), w)){
                    return tpos;
                }
                tpos += 1;
            }
            return -1;
        }
        public SuffixIterator () { pos = 0 ; }
        public boolean hasNext () { return GetNext() != -1; }
        public Integer next () {
            int tpos = GetNext();
            pos = tpos + 1;
            return tpos;
        }
    }
}