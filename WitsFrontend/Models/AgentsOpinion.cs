using System.ComponentModel.DataAnnotations;
using Postgrest.Attributes;
using Postgrest.Models;

namespace WitsFrontend.Models;
    
[Table("AgentsOpinions")]
public class AgentOpinion : BaseModel
{
    [PrimaryKey("id", false)]
    public int Id { get; set; }

    [Column("agent_id")]
    [Required]
    public int AgentId { get; set; }

    [Column("subject")]
    [Required]
    public string Subject { get; set; }

    [Column("opinion")]
    [Required]
    public string Opinion { get; set; }

    [Column("embedding")]
    [Required]
    public List<float> Embedding { get; set; }
}
