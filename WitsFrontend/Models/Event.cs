using System.ComponentModel.DataAnnotations;
using Postgrest.Attributes;
using Postgrest.Models;

namespace WitsFrontend.Models;

[Table("Events")]
public class Event : BaseModel
{
    [PrimaryKey("id", false)]
    public int Id { get; set; }

    [Column("created_at")]
    [Required]
    public DateTime CreatedAt { get; set; }

    [Column("event_type")]
    [Required]
    public int EventType { get; set; }

    [Column("event_details")]
    [Required]
    public string EventDetails { get; set; }

    [Column("embedding")]
    [Required]
    public List<float> Embedding { get; set; }
}
