using System.ComponentModel.DataAnnotations;
using Postgrest.Attributes;
using Postgrest.Models;

namespace WitsFrontend.Models;


[Table("organisations")]
public class Organisation : BaseModel
{
    [PrimaryKey("id", false)]
    public int Id { get; set; }

    [Column("name")]
    [Required]
    public string Name { get; set; }

    [Column("type")]
    [Required]
    public string Type { get; set; }

    [Column("description")]
    [Required]
    public string Description { get; set; }

    [Column("mission")]
    [Required]
    public string Mission { get; set; }
}
