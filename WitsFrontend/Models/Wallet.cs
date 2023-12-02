using System.ComponentModel.DataAnnotations;
using Postgrest.Attributes;
using Postgrest.Models;

namespace WitsFrontend.Models;

[Table("Wallet")]
public class Wallet : BaseModel
{
    [PrimaryKey("id", false)]
    public int Id { get; set; }

    [Column("agent_id")]
    [Required]
    public int AgentId { get; set; }

    [Column("asset_id")]
    [Required]
    public int AssetId { get; set; }

    [Column("balance")]
    [Required]
    public decimal Balance { get; set; }
}
