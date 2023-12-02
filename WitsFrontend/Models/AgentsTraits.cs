using Postgrest.Attributes;
using Postgrest.Models;

namespace WitsFrontend.Models;

[Table("agentstraits")]
public class AgentTrait : BaseModel
{
    [PrimaryKey("agent_id")]
    public int AgentId { get; set; }

    [PrimaryKey("trait_id")]
    public int TraitId { get; set; }

    [Column("is_positive")]
    public bool IsPositive { get; set; }
}
