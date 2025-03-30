package task2;

import java.util.Iterator;

public class StringList implements Iterable<String> {
    private String[] strings;

    public void setStrings(String[] s){
        this.strings = s;
    }
    public StringList(String[] s){
        this.strings = s;
    }
    private class StringListIterator implements Iterator<String> {
        private int stringIndex;
        public StringListIterator () {stringIndex = 0;}


        public boolean hasNext () {
            for (int j = stringIndex; j < strings.length - 1; j++) {
                for (int i = 0; i < strings[j].length(); i++) {
                    String sub = strings[j].substring(i);
                    if (strings[j+1].startsWith(sub)){
                        return true;
                    }
                }
            }
            return false;
        }
        public String next () {
            for (; stringIndex < strings.length - 1; stringIndex++) {
                for (int i = 0; i < strings[stringIndex].length(); i++) {
                    String sub = strings[stringIndex].substring(i);
                    if (strings[stringIndex+1].startsWith(sub)){
                        stringIndex += 1;
                        return sub;
                    }
                }
            }
            return "";
        }
    }
    @Override
    public Iterator<String> iterator() {
        return new StringListIterator();
    }
}
