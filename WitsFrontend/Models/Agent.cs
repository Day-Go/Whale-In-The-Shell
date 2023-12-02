using System.ComponentModel.DataAnnotations;
using Postgrest.Attributes;
using Postgrest.Models;

namespace WitsFrontend.Models;


[Table("agents")]
public class Agent : BaseModel
{
    [PrimaryKey("id", false)]
    public int Id { get; set; }

    [Column("name")]
    [Required]
    public string Name { get; set; }

    [Column("occupation")]
    [Required]
    public string Occupation { get; set; }

    [Column("handle")]
    [Required]
    public string Handle { get; set; }

    [Column("biography")]
    [Required]
    public string Biography { get; set; }

    [Column("nationality")]
    [Required]
    public string Nationality { get; set; }

    [Column("investment_style")]
    public string InvestmentStyle { get; set; }

    [Column("risk_tolerance")]
    public string RiskTolerance { get; set; }

    [Column("goals")]
    public string Goals { get; set; }

    [Column("communication_style")]
    public string CommunicationStyle { get; set; }
}
