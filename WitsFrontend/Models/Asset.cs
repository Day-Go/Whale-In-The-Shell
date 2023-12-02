using System.ComponentModel.DataAnnotations;
using Postgrest.Attributes;
using Postgrest.Models;

namespace WitsFrontend.Models;

[Table("Assets")]
public class Asset : BaseModel
{
    [PrimaryKey("id", false)]
    public int Id { get; set; }

    [Column("ticker")]
    [Required]
    public string Ticker { get; set; }

    [Column("name")]
    [Required]
    public string Name { get; set; }

    [Column("circulating_supply")]
    public decimal CirculatingSupply { get; set; }

    [Column("max_supply")]
    public decimal MaxSupply { get; set; }

    [Column("market_cap")]
    [Required]
    public decimal MarketCap { get; set; }

    [Column("price")]
    [Required]
    public decimal Price { get; set; }

    [Column("volume_24h")]
    [Required]
    public decimal Volume24h { get; set; }

    [Column("change_24h")]
    [Required]
    public decimal Change24h { get; set; }

    [Column("all_time_high")]
    public decimal AllTimeHigh { get; set; }

    [Column("all_time_low")]
    public decimal AllTimeLow { get; set; }
}
