using System.ComponentModel.DataAnnotations;
using Postgrest.Attributes;
using Postgrest.Models;

namespace WitsFrontend.Models;

[Table("products")]
public class Product : BaseModel
{
    [PrimaryKey("id", false)]
    public int Id { get; set; }

    [Column("org_id")]
    [Required]
    public int OrgId { get; set; }

    [Column("name")]
    [Required]
    public string Name { get; set; }

    [Reference(typeof(Organisation))] 
    public Organisation Organisation { get; set; }
}
