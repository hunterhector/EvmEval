package evmeval;

/**
 * A token annotation.
 * 
 * @author Jun Araki
 */
public class Token extends ElementalAnnotation {

  /**
   * Public constructor.
   * 
   * @param doc
   * @param begin
   * @param end
   */
  public Token(Document doc, int begin, int end) {
    super(doc, begin, end, "Token");
  }

}
