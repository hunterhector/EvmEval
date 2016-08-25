package converter;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.io.AbstractReader;
import net.junaraki.annobase.type.concept.Event;
import net.junaraki.annobase.type.element.EventMention;
import org.apache.commons.io.FileUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.text.WordUtils;
import org.jdom2.Document;
import org.jdom2.Element;
import org.jdom2.input.SAXBuilder;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

public abstract class LdcXmlReader extends AbstractReader {

    /**
     * For reading the event nugget data in LDC2015E73 V2
     */
    public static final String INPUT_MODE_EVENT_NUGGET = "event-nugget";

    /**
     * An XML parser; input annotation files are given in the XML format
     */
    private SAXBuilder builder;

    private File annDir;

    private String textFileExt, annFileExt;

    private boolean detagText;

    private String inputMode;

    public LdcXmlReader(File annDir, String textFileExt, String annFileExt, boolean detagText,
                        String inputMode) {
        this.annDir = annDir;
        this.textFileExt = textFileExt;
        this.annFileExt = annFileExt;
        this.detagText = detagText;
        this.inputMode = inputMode;
        builder = new SAXBuilder();
        builder.setDTDHandler(null);
    }

    @Override
    public AnnotationBase read(File file) throws Exception {
        String docText = FileUtils.readFileToString(file);
        if (detagText) {
            docText = Detagger.detag(docText, true);
        }

        String fileName = file.getName();
        String baseName = fileName.substring(0, fileName.length() - textFileExt.length() - 1);

        // Annotate gold standard annotations.
        File inputAnnFile = new File(annDir, baseName + "." + annFileExt);

        AnnotationBase annBase = new AnnotationBase(docText, baseName);
        parse(annBase, inputAnnFile);

        return consume(annBase, docText, baseName);
    }

    protected abstract AnnotationBase consume(AnnotationBase annBase, String docText, String baseName);

    private void parse(AnnotationBase annBase, File file) throws Exception {
        Document doc = builder.build(file);

        Element rootElm = doc.getRootElement();
        if (INPUT_MODE_EVENT_NUGGET.equals(inputMode)) {
            annotateEventMentions(annBase, rootElm);
        } else {
            annotateEvents(annBase, rootElm.getChild("hoppers").getChildren("hopper"));
        }
    }

    /**
     * Annotates events. This method calls a method to annotate event mentions.
     *
     * @param annBase
     * @param hopperElms
     */
    private void annotateEvents(AnnotationBase annBase, List<Element> hopperElms) {
        for (Element hopperElm : hopperElms) {
            Event event = new Event(annBase);
            String eventIdStr = hopperElm.getAttributeValue("id");
            if (!eventIdStr.startsWith("h-") && StringUtils.isNumeric(eventIdStr.substring(2))) {
                Logger.warn(String.format("Invalid event id: %s", eventIdStr));
            }
            int eventId = Integer.parseInt(eventIdStr.substring(2));
            event.setId(eventId);
            event.addToBase();

            // Extract event mentions belonging to this event.
            List<EventMention> evms = annotateEventMentions(annBase, hopperElm);
            event.setEventMentions(evms);
            for (EventMention evm : evms) {
                evm.setEvent(event);
            }
        }
    }

    /**
     * Annotates event mentions from the given event data structure.
     *
     * @param annBase
     * @param parentElm
     */
    private List<EventMention> annotateEventMentions(AnnotationBase annBase, Element parentElm) {
        List<EventMention> evms = new ArrayList<EventMention>();

        // Annotate event mentions.
        for (Element evmElm : parentElm.getChildren("event_mention")) {
            // First annotate event mention, and then attach things to it.
            String evmIdStr = evmElm.getAttributeValue("id");
            if (!evmIdStr.startsWith("em-") && StringUtils.isNumeric(evmIdStr.substring(3))) {
                Logger.warn(String.format("Invalid event mention id: %s", evmIdStr));
            }
            int evmId = Integer.parseInt(evmIdStr.substring(3));
            String type = WordUtils.capitalize(evmElm.getAttributeValue("type"));
            String subtype = WordUtils.capitalize(evmElm.getAttributeValue("subtype"));
            switch (subtype) {
                case "Transfermoney":
                    // Logger.debug("Transfer-Money");
                    subtype = "Transfer-Money";
                    break;
                case "Transferownership":
                    // Logger.debug("Transfer-Ownership");
                    subtype = "Transfer-Ownership";
                    break;
                case "Startorg":
                    // Logger.debug("Start-Org");
                    subtype = "Start-Org";
                    break;
                case "Endorg":
                    // Logger.debug("End-Org");
                    subtype = "End-Org";
                    break;
                case "Declarebankruptcy":
                    // Logger.debug("Declare-Bankruptcy");
                    subtype = "Declare-Bankruptcy";
                    break;
                case "Mergeorg":
                    // Logger.debug("Merge-Org");
                    subtype = "Merge-Org";
                    break;
                case "Startposition":
                    // Logger.debug("Start-Position");
                    subtype = "Start-Position";
                    break;
                case "Endposition":
                    // Logger.debug("End-Position");
                    subtype = "End-Position";
                    break;
                case "Arrestjail":
                    // Logger.debug("Arrest-Jail");
                    subtype = "Arrest-Jail";
                    break;
                case "Chargeindict":
                    // Logger.debug("Charge-Indict");
                    subtype = "Charge-Indict";
                    break;
                case "Releaseparole":
                    // Logger.debug("Release-Parole");
                    subtype = "Release-Parole";
                    break;
                case "Trialhearing":
                    // Logger.debug("Trial-Hearing");
                    subtype = "Trial-Hearing";
                    break;
                case "Transportartifact":
                    // Logger.debug("Transport-Artifact");
                    subtype = "Transport-Artifact";
                    break;
                case "Transportperson":
                    // Logger.debug("Transport-Person");
                    subtype = "Transport-Person";
                    break;
                default:
                    // Do nothing.
            }
            String eventType = type + "_" + subtype;
            String realis = WordUtils.capitalize(evmElm.getAttributeValue("realis"));

            Element triggerElm = evmElm.getChild("trigger");
            int begin = Integer.parseInt(triggerElm.getAttributeValue("offset"));
            int length = Integer.parseInt(triggerElm.getAttributeValue("length"));
            int end = begin + length;
            String evmStr = triggerElm.getValue();

            EventMention evm = annotateEventMention(annBase, begin, end, evmId, eventType, realis);
            if (!evmStr.equals(evm.getText().replace('\n', ' '))) {
                Logger.warn(String.format(
                        "Invalid offset %d, %d of event mention [%s] for string [%s] at doc [%s]", begin,
                        end, evm.getText(), evmStr, annBase.getSourceDocument().getId()));
            }

            evms.add(evm);
        }

        return evms;
    }

    /**
     * Annotates an event mention.
     *
     * @param annBase
     * @param begin
     * @param end
     * @param evmId
     * @param eventType
     * @param realis
     * @return
     */
    private EventMention annotateEventMention(AnnotationBase annBase, int begin, int end, int evmId,
                                              String eventType, String realis) {
        EventMention evm = new EventMention(annBase, begin, end);
        evm.setId(evmId);
        evm.setEventType(eventType);
        evm.setEpistemicStatus(realis);
        evm.addToBase();

        return evm;
    }

}
