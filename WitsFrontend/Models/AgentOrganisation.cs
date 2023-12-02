using System.ComponentModel.DataAnnotations;
using Postgrest.Attributes;
using Postgrest.Models;

namespace WitsFrontend.Models;


[Table("AgentsOrganisations")]
public class AgentOrganisation : BaseModel
{
    [PrimaryKey("agent_org_id", false)]
    public int AgentOrgId { get; set; }

    [Column("agent_id")]
    [Required]
    public int AgentId { get; set; }

    [Column("org_id")]
    [Required]
    public int OrgId { get; set; }

    [Column("opinion")]
    public string Opinion { get; set; }
}
