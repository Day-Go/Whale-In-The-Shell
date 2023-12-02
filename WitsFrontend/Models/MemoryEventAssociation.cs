using System.ComponentModel.DataAnnotations;
using Postgrest.Attributes;
using Postgrest.Models;

namespace WitsFrontend.Models;


[Table("MemoryEventAssociations")]
public class MemoryEventAssociations : BaseModel
{
    [Column("memory_id")]
    [Required(ErrorMessage = "Memory ID is required.")]
    public int MemoryId { get; set; }

    [Column("event_id")]
    [Required(ErrorMessage = "Event ID is required.")]
    public int EventId { get; set; }
}
