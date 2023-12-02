using System.ComponentModel.DataAnnotations;
using Postgrest.Attributes;
using Postgrest.Models;

namespace WitsFrontend.Models;

[Table("prompts")]
public class Prompt : BaseModel
{
    [PrimaryKey("id", false)]
    public int Id { get; set; }

    [Column("name")]
    [Required]
    public string Name { get; set; }

    [Column("content")]
    [Required]
    public string Content { get; set; }
}
