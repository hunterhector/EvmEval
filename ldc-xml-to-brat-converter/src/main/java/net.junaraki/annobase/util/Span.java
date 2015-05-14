package net.junaraki.annobase.util;

import java.io.Serializable;
import java.util.Arrays;

/**
 * A generic span with a begin offset and an end one.
 * 
 * @author Jun Araki
 */
public class Span implements Comparable<Span>, Serializable {

  private static final long serialVersionUID = -8397348259778909906L;

  protected int begin;

  protected int end;

  /**
   * Public constructor.
   * 
   * @param begin
   * @param end
   */
  public Span(int begin, int end) {
    if (begin > end) {
      throw new IllegalArgumentException("Begin index must be not larger than end index!");
    }

    this.begin = begin;
    this.end = end;
  }

  public boolean isEmpty() {
    return (begin == end);
  }

  @Override
  public int hashCode() {
    return Arrays.hashCode(new int[] { this.begin, this.end });
  }

  @Override
  public boolean equals(Object obj) {
    if (obj == this) {
      return true;
    }
    if (!(obj instanceof Span)) {
      return false;
    }

    Span that = (Span) obj;
    return (this.begin == that.begin && this.end == that.end);
  }

  @Override
  public String toString() {
    return String.format("Span [%d,%d]", begin, end);
  }

  /**
   * Returns true if this span covers the given span completely.
   * 
   * @param that
   * @return
   */
  public boolean covers(Span that) {
    if (this.begin <= that.begin && this.end >= that.end) {
      return true;
    }
    return false;
  }

  /**
   * Returns true if this span is covered by the given span completely.
   * 
   * @param that
   * @return
   */
  public boolean coveredBy(Span that) {
    return that.covers(this);
  }

  /**
   * Returns if this span overlaps the given span to some degree.
   * 
   * @param that
   * @return
   */
  public boolean overlap(Span that) {
    if (that.begin >= this.end || that.end <= this.begin) {
      return false;
    }

    return true;
  }

  /**
   * A span precedes another one if the former's beginning precedes the latter's, or the former's
   * end precedes the latter's if the former's beginning is equal to the latter's.
   * 
   * @param that
   */
  @Override
  public int compareTo(Span that) {
    if (this.begin < that.begin) {
      return -1;
    } else if (this.begin > that.begin) {
      return 1;
    }

    if (this.end < that.end) {
      return -1;
    } else if (this.end > that.end) {
      return 1;
    }

    return 0;
  }

  public int getBegin() {
    return begin;
  }

  public int getEnd() {
    return end;
  }

}
