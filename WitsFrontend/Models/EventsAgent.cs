using System.ComponentModel.DataAnnotations;
using Postgrest.Attributes;
using Postgrest.Models;

namespace WitsFrontend.Models;

[Table("EventsAgents")]
public class EventsAgents : BaseModel
{
    [PrimaryKey("event_agent_id", false)]
    public int EventAgentId { get; set; }

    [Column("event_id")]
    [Required(ErrorMessage = "Event ID is required.")]
    public int EventId { get; set; }

    [Column("agent_id")]
    [Required(ErrorMessage = "Agent ID is required.")]
    public int AgentId { get; set; }
}
