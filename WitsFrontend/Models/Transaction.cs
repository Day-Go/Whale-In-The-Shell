using System.ComponentModel.DataAnnotations;
using Postgrest.Attributes;
using Postgrest.Models;

namespace WitsFrontend.Models;


[Table("Transactions")]
public class Transaction : BaseModel
{
    [PrimaryKey("id", false)]
    public int Id { get; set; }

    [Column("wallet_id")]
    [Required]
    public int WalletId { get; set; }

    [Column("type")]
    [Required]
    public string Type { get; set; } // 'buy' or 'sell'

    [Column("asset_id")]
    [Required]
    public int AssetId { get; set; }

    [Column("amount")]
    [Required]
    public decimal Amount { get; set; }

    [Column("price")]
    [Required]
    public decimal Price { get; set; }

    [Column("timestamp")]
    [Required]
    public DateTime Timestamp { get; set; }
}
