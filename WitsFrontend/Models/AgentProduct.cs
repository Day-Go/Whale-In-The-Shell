using System.ComponentModel.DataAnnotations;
using Postgrest.Attributes;
using Postgrest.Models;

namespace WitsFrontend.Models;


[Table("AgentsProducts")]
public class AgentsProducts : BaseModel
{
    [PrimaryKey("agent_product_id", false)]
    public int AgentProductId { get; set; }

    [Column("agent_id")]
    [Required(ErrorMessage = "Agent ID is required.")]
    public int AgentId { get; set; }

    [Column("product_id")]
    [Required(ErrorMessage = "Product ID is required.")]
    public int ProductId { get; set; }

    [Column("opinion")]
    public string Opinion { get; set; }
}
