package evmeval;

/**
 * This class represents a span within an event mention. Note that the event mention span is not
 * exactly the same as an event mention; an event mention can be annotated over discontinuous
 * multiple tokens.
 * 
 * @author Jun Araki
 */
public class EventMentionSpan extends ElementalAnnotation {

  /**
   * Public constructor.
   * 
   * @param doc
   * @param begin
   * @param end
   */
  public EventMentionSpan(Document doc, int begin, int end) {
    super(doc, begin, end, "EventMentionSpan");
  }

}
