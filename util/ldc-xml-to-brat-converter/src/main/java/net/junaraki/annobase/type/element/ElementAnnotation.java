package net.junaraki.annobase.type.element;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.AbstractAnnotation;
import net.junaraki.annobase.util.Span;

public abstract class ElementAnnotation extends AbstractAnnotation implements
        Comparable<ElementAnnotation> {

  private static final long serialVersionUID = -5503304936437696074L;

  public static final String SPAN_SEPARATOR = "#";

  /**
   * The offset of this annotation that can have multiple (discontinuous) spans. The order of spans
   * matters.
   */
  protected final List<Span> spans;

  /**
   * Public constructor. The begin offset is inclusive, starting with 0, and the end offset is
   * exclusive.
   * 
   * @param annBase
   * @param begin
   * @param end
   */
  public ElementAnnotation(AnnotationBase annBase, int begin, int end) {
    super(annBase);
    spans = new ArrayList<Span>();
    spans.add(new Span(begin, end));
  }

  @Override
  public boolean equals(Object obj) {
    if (obj == this) {
      return true;
    }
    // Expect super classes to compare 'annBase' and 'typeName'.
    if (!super.equals(obj)) {
      return false;
    }
    if (!(obj instanceof ElementAnnotation)) {
      return false;
    }

    ElementAnnotation that = (ElementAnnotation) obj;
    if (!spans.equals(that.getSpans())) {
      return false;
    }

    return true;
  }

  @Override
  public int hashCode() {
    int result = hashCode;
    if (result == 0) {
      result = 17;
      result = 31 * result + super.hashCode();
      result = 31 * result + spans.hashCode();
      hashCode = result;
    }

    return result;
  }

  @Override
  public String toString() {
    return String.format("%s [%s,%d,%d] [%s]", getTypeName(), getAnnotationBase()
            .getSourceDocument().getId(), getBegin(), getEnd(), getText());
  }

  /**
   * An element annotation precedes another one if the former's begin precedes the latter's, or the
   * former's end precedes the latter's if the former's begin is equal to the latter's.
   * 
   * @param that
   */
  @Override
  public int compareTo(ElementAnnotation that) {
    if (getBegin() < that.getBegin()) {
      return -1;
    } else if (this.getBegin() > that.getBegin()) {
      return 1;
    }

    if (this.getEnd() < that.getEnd()) {
      return -1;
    } else if (this.getEnd() > that.getEnd()) {
      return 1;
    }

    return 0;
  }

  /**
   * Returns text covered by this annotation. Note that the text contains span separators if the
   * annotation has multiple spans.
   * 
   * @return
   */
  public String getText() {
    if (numSpans() == 1) {
      return annBase.getSourceDocument().getText(spans.get(0));
    }

    StringBuilder buf = new StringBuilder();
    for (int i = 0; i < spans.size(); i++) {
      if (i > 0) {
        buf.append(SPAN_SEPARATOR);
      }
      buf.append(spans.get(i));
    }
    return buf.toString();
  }

  public String getLowerCaseText() {
    return getText().toLowerCase();
  }

  /**
   * Returns a list of texts covered by this annotation.
   * 
   * @return
   */
  public List<String> getTexts() {
    List<String> texts = new ArrayList<String>();
    for (Span span : spans) {
      texts.add(annBase.getDocumentText().substring(span.getBegin(), span.getEnd()));
    }
    return texts;
  }

  public List<String> getLowerCaseTexts() {
    List<String> texts = getTexts();
    for (String text : texts) {
      text = text.toLowerCase();
    }
    return texts;
  }

  /**
   * Returns the beginning of the first span in this annotation.
   * 
   * @return
   */
  public int getBegin() {
    return spans.get(0).getBegin();
  }

  /**
   * Returns the end of the last span in this annotation.
   * 
   * @return
   */
  public int getEnd() {
    return spans.get(spans.size() - 1).getEnd();
  }

  /**
   * Adds a span with the given offsets to this annotation.
   * 
   * @param begin
   * @param end
   */
  public void addSpan(int begin, int end) {
    spans.add(new Span(begin, end));
  }

  public List<Span> getSpans() {
    return spans;
  }

  public int numSpans() {
    return spans.size();
  }

  /**
   * Returns true if this annotation has multiple spans.
   * 
   * @return
   */
  public boolean hasMultipleSpans() {
    if (numSpans() == 1) {
      return false;
    }
    return true;
  }

  /**
   * Returns true if this annotation covers the given element annotation.
   * 
   * @param ann
   * @return
   */
  public boolean cover(ElementAnnotation ann) {
    return ann.coveredBy(this);
  }

  /**
   * Returns true if this annotation covers one of the given element annotations.
   * 
   * @param anns
   * @return
   */
  public <T extends ElementAnnotation> boolean coverOneOf(Collection<T> anns) {
    for (T ann : anns) {
      if (cover(ann)) {
        return true;
      }
    }

    return false;
  }

  /**
   * Returns an annotation that this annotation covers. Note that this method only finds the first
   * annotation that the annotation covers.
   * 
   * @param anns
   * @return
   */
  public <T extends ElementAnnotation> T findAnnotationCoveringOneOf(Collection<T> anns) {
    for (T ann : anns) {
      if (cover(ann)) {
        return ann;
      }
    }

    return null;
  }

  /**
   * Returns true if this annotation is covered by the given element annotation.
   * 
   * @param ann
   * @return
   */
  public boolean coveredBy(ElementAnnotation ann) {
    for (Span thisSpan : getSpans()) {
      boolean flag = false;
      for (Span thatSpan : ann.getSpans()) {
        // Found a span which is covered by a span in the given annotation.
        if (thisSpan.coveredBy(thatSpan)) {
          flag = true;
          break;
        }
      }

      if (!flag) {
        // This annotation has a span which is not covered by any span in the given annotation.
        return false;
      }
    }

    return true;
  }

  /**
   * Returns true if this annotation is covered by the text span specified with the given offsets.
   * 
   * @param begin
   * @param end
   * @return
   */
  public boolean coveredBy(int begin, int end) {
    for (Span span : getSpans()) {
      if (span.getBegin() < begin || span.getEnd() > end) {
        return false;
      }
    }

    return true;
  }

  /**
   * Returns true if this annotation is covered by one of the given element annotations.
   * 
   * @param anns
   * @return
   */
  public <T extends ElementAnnotation> boolean coveredByOneOf(Collection<T> anns) {
    for (T ann : anns) {
      if (coveredBy(ann)) {
        return true;
      }
    }

    return false;
  }

  /**
   * Returns an annotation covered by this annotation. Note that this method only finds the first
   * annotation covered by the annotation.
   * 
   * @param anns
   * @return
   */
  public <T extends ElementAnnotation> T findAnnotationCoveredByOneOf(Collection<T> anns) {
    for (T ann : anns) {
      if (coveredBy(ann)) {
        return ann;
      }
    }

    return null;
  }

  /**
   * Returns true if this annotation overlaps the given element annotation.
   * 
   * @param ann
   * @return
   */
  public boolean overlap(ElementAnnotation ann) {
    for (Span thisSpan : getSpans()) {
      boolean flag = false;
      for (Span thatSpan : ann.getSpans()) {
        // Found a span which overlaps a span in the given annotation.
        if (thisSpan.overlap(thatSpan)) {
          flag = true;
          break;
        }
      }

      if (!flag) {
        // This annotation has a span which is not overlapped by any span in the given annotation.
        return false;
      }
    }

    return true;
  }

  /**
   * Returns true if this annotation has the same span as the given element annotation.
   * 
   * @param ann
   * @return
   */
  public boolean hasSameSpan(ElementAnnotation ann) {
    if (numSpans() != ann.numSpans()) {
      return false;
    }

    for (int i = 0; i < numSpans(); i++) {
      if (!spans.get(i).equals(ann.getSpans().get(i))) {
        return false;
      }
    }

    return true;
  }

  /**
   * Returns true if this annotation has the same span as any of the given element annotations.
   * 
   * @param anns
   * @return
   * 
   * @param anns
   * @return
   */
  public <T extends ElementAnnotation> boolean hasSameSpanAsOneOf(Collection<T> anns) {
    for (T ann : anns) {
      if (hasSameSpan(ann)) {
        return true;
      }
    }

    return false;
  }

  /**
   * Returns true if this annotation precedes the given annotation.
   * 
   * @param ann
   * @return
   */
  public boolean precedes(ElementAnnotation ann) {
    return (getEnd() <= ann.getBegin());
  }

  /**
   * Returns true if this annotation follows the given annotation.
   * 
   * @param ann
   * @return
   */
  public boolean follows(ElementAnnotation ann) {
    return (getBegin() >= ann.getEnd());
  }

}
