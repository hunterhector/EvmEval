package evmeval;

/**
 * An elemental annotation.
 * 
 * @author Jun Araki
 */
public class ElementalAnnotation extends Span {

  /** A document where this annotation is annotated */
  private Document doc;

  /** The name of an annotation type. */
  private String typeName;

  /**
   * Public constructor.
   * 
   * @param doc
   * @param begin
   * @param end
   * @param typeName
   */
  public ElementalAnnotation(Document doc, int begin, int end, String typeName) {
    super(begin, end);
    this.doc = doc;
    this.typeName = typeName;
  }

  @Override
  public String toString() {
    return String.format("%s [%d,%d] [%s]", typeName, begin, end, getCoveredText());
  }

  public String getCoveredText() {
    return doc.getText().substring(begin, end);
  }

  public Document getDocument() {
    return doc;
  }

  public String getTypeName() {
    return typeName;
  }

}
