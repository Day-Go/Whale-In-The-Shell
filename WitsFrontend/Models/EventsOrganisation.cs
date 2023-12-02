using System.ComponentModel.DataAnnotations;
using Postgrest.Attributes;
using Postgrest.Models;

namespace WitsFrontend.Models;


[Table("EventsOrganisations")]
public class EventsOrganisations : BaseModel
{
    [PrimaryKey("event_org_id", false)]
    public int EventOrgId { get; set; }

    [Column("event_id")]
    [Required(ErrorMessage = "Event ID is required.")]
    public int EventId { get; set; }

    [Column("org_id")]
    [Required(ErrorMessage = "Organisation ID is required.")]
    public int OrgId { get; set; }
}
