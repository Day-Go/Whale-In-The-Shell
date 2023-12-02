using System.ComponentModel.DataAnnotations;
using Postgrest.Attributes;
using Postgrest.Models;

namespace WitsFrontend.Models;


[Table("Memories")]
public class Memory : BaseModel
{
    [PrimaryKey("id", false)]
    public int Id { get; set; }

    [Column("agent_id")]
    [Required]
    public int AgentId { get; set; }

    [Column("memory_details")]
    [Required]
    public string MemoryDetails { get; set; }

    [Column("created_at")]
    [Required]
    public DateTime CreatedAt { get; set; }

    [Column("embedding")]
    public List<float> Embedding { get; set; }
}
