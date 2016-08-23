package converter;

import com.google.common.base.Joiner;
import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.concept.Event;
import net.junaraki.annobase.type.element.EntityMention;
import net.junaraki.annobase.type.element.EventMention;

import java.util.ArrayList;
import java.util.List;

/**
 * Created with IntelliJ IDEA.
 * Date: 8/22/16
 * Time: 10:06 PM
 *
 * @author Zhengzhong Liu
 */
public class TbfAnnotationBase extends AnnotationBase {
    private int annId, evmId;

    public TbfAnnotationBase(String text) {
        super(text);
    }

    public TbfAnnotationBase(String text, String docId) {
        super(text, docId);
    }

    @Override
    protected void initialize() {
        super.initialize();
        annId = evmId = 1;
    }

    public void consume(AnnotationBase annBase) {
        if (!srcDoc.equals(annBase.getSourceDocument())) {
            throw new IllegalArgumentException(
                    "The given annotation base has a different source document.");
        }

        annMap = annBase.getAnnotationMap();
        for (EntityMention enm : getEntityMentions()) {
            enm.setId(annId); // Entity ID is equal to annotation ID.
            annId++;
        }
        for (EventMention evm : getEventMentions()) {
            if (evm.getId() <= 0) {
                evm.setId(evmId);
                evmId++;
            }
            annId++;
        }
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();

        sb.append("#BeginOfDocument ").append(srcDoc.getId()).append("\n");

        Logger.info("There are " + getEventMentions().size() + " event mentions.");

        for (EventMention eventMention : getEventMentions()) {
            sb.append(String.format("rich_ere\t%s\tE%d\t%d,%d\t%s\t%s\t%s\n", srcDoc.getId(), eventMention.getId(),
                    eventMention.getBegin(), eventMention.getEnd(), eventMention.getText(), eventMention.getEventType
                            (), eventMention.getEpistemicStatus()));
        }


        for (Event event : getEvents()) {
            List<String> mentionIds = new ArrayList<>();
            List<EventMention> containedMentions = event.getEventMentions();

            if (containedMentions.size() > 1) {
                for (EventMention eventMention : containedMentions) {
                    mentionIds.add("E" + eventMention.getId());
                }
                sb.append("@Coreference\t").append("C").append(event.getId()).append("\t").append(Joiner.on(",").join
                        (mentionIds)).append("\n");
            }
        }

        sb.append("#EndOfDocument\n");

        return sb.toString();
    }
}
