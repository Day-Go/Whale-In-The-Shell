using System.ComponentModel.DataAnnotations;
using Postgrest.Attributes;
using Postgrest.Models;

namespace WitsFrontend.Models;


[Table("EventsProducts")]
public class EventsProducts : BaseModel
{
    [PrimaryKey("event_product_id", false)]
    public int EventProductId { get; set; }

    [Column("event_id")]
    [Required(ErrorMessage = "Event ID is required.")]
    public int EventId { get; set; }

    [Column("product_id")]
    [Required(ErrorMessage = "Product ID is required.")]
    public int ProductId { get; set; }
}
