"""合同模板种子数据"""
import logging

from sqlalchemy import select

from app.database import async_session_factory
from app.models.contract_template import ContractTemplate

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 房屋租赁合同 HTML 模板
# ---------------------------------------------------------------------------
LEASE_CONTRACT_HTML = """
<h1 style="text-align:center;">房屋租赁合同</h1>

<p>甲方（出租方）：{{partyAName}}<br/>
身份证号码：{{partyAIdCard}}</p>

<p>乙方（承租方）：{{partyBName}}<br/>
身份证号码：{{partyBIdCard}}</p>

<p>根据《中华人民共和国合同法》、《房屋租赁条例》等法律、法规和规定，甲、乙双方在平等、自愿、公平和诚实的基础上，经协商一致，就乙方承租甲方可依法出租的房屋事宜，订立本合同。</p>

<h2>一、出租房屋情况和租赁用途</h2>

<p>甲方将座落在{{houseAddress}}的房屋（简称该房屋）出租给乙方，该房屋建筑面积为{{houseArea}}平方米，房屋用途为居住。并已告知该房屋【已】【未】设定抵押。</p>

<p>乙方向甲方承诺，租赁该房屋作为居住使用。</p>

<p>该房屋的公用或合用部位的使用范围、条件和要求，现有装修、附属设施、设备状况及需约定的有关事宜，由甲、乙双方在本合同补充条款中加以列明。</p>

<p>甲、乙双方同意附件为甲方向乙方交付该房屋和本合同终止时乙方向甲方返还该房屋的验收依据。</p>

<h2>二、交付日期和租赁期限</h2>

<p>甲乙双方约定，甲方于{{deliverDate}}前向乙方交付该房屋。</p>

<p>租赁期自{{leaseStartDate}}起至{{leaseEndDate}}止。</p>

<p>租赁期满，乙方若需继续承租该房屋，则应于租赁期届满前{{renewalNoticeMonths}}个月，向甲方提出续租书面要求。经甲方同意后，双方应重新签订租赁合同。</p>

<h2>三、租金、支付方式和期限</h2>

<p>甲乙双方约定，该房屋月租金为（人民币{{monthlyRent}}元）（大写：{{monthlyRentCapital}}）。</p>

<p>乙方支付租金的方式是{{paymentMethod}}。如果逾期支付，逾期一日则乙方需按月租金的5%支付违约金给甲方。</p>

<h2>四、保证金和其他费用</h2>

<p>甲乙双方约定，甲方交付该房屋时，乙方应向甲方支付房屋租赁保证金。</p>

<p>保证金为{{depositMonths}}个月租金，即{{depositAmount}}元。保证金收取后，甲方应向乙方开具收款凭证。租赁关系终止时，甲方收取的房屋保证金用于抵充合同的约定由乙方承担的费用外，剩余部分无息归还乙方。</p>

<p>租赁期间，使用该房屋所发生的水、电、煤、通信、空调、数字电视、{{otherFees}}等一切费用由乙方承担。</p>

<h2>五、房屋使用要求和维修责任</h2>

<p>5-1 租赁期间，乙方按照房屋物业管理要求和甲方要求合理使用并爱护该房屋及其附属设施，鉴于本合同房屋装修由乙方全权负责实施及支付装修费用情况，因此对房屋及其实施装修责任由乙方自行承担责任及费用。</p>

<h2>六、房屋返还时的状态</h2>

<p>6-1 除甲方同意乙方续租外，乙方应在合同的租赁期满后当日内返还该房屋，未经甲方同意逾期返还房屋的，每逾期一日，乙方应按月租金的5%每日向甲方支付房屋占用期间的使用费用。</p>

<h2>七、解除本合同的条件</h2>

<p>甲乙双方同意在租赁期内，有下列情形之一的，本合同终止，双方互不承担责任：</p>
<ol>
<li>该房屋因社会公共利益被依法征用的；</li>
<li>该房屋因城市建设需要被依法列入房屋拆迁许可范围的；</li>
<li>该房屋在租赁期间因不可抗力导致毁损、灭失的；</li>
<li>甲方已告知乙方该房屋出租前已设定抵押并可能于租赁期限内被处分，现被处分的。</li>
</ol>

<p>甲乙双方同意，有下列情形之一的，一方可书面通知另一方解除本合同，违反合同的一方，应向另一方按月租金的壹倍支付违约金：</p>
<ol>
<li>甲方未按时交付该房屋，经乙方催告后五天内仍未交付的；</li>
<li>甲方交付的该房屋不符合本合同约定的，致使不能实现租赁目的的或甲方交付的房屋存缺陷、危及乙方安全的；</li>
<li>因乙方原因造成房屋主体结构损坏的；</li>
<li>乙方在租赁期间在甲方房屋内发生违法事件，所出现的法律后果由乙方承担，如若情节严重，甲方有权终止合同，乙方需向甲方做出相应赔偿。</li>
</ol>

<h2>八、解决争议的方式</h2>

<p>8-1 甲、乙双方在履行本合同过程中若发生争议，应协商解决，协商不成的双方同意选择下列第{{disputeMethod}}种方式解决：</p>
<ol>
<li>提交本市仲裁委员会仲裁；</li>
<li>依法向人民法院起诉。</li>
</ol>

<h2>九、其它条款</h2>

<p>租赁期间，甲方需抵押该房屋，应书面告知乙方，并向乙方承诺该房屋抵押后当事人协议以折价、变卖方式处分该房屋前五日书面征询乙方购买该房屋的意见。</p>

<p>本合同未尽事宜，经甲、乙双方协商一致，可订立补充条款。本合同补充条款为本合同不可分割的一部分，本合同及其补充条款内空格并且填写的文字与铅印文字具有同等效力。</p>

<p>甲、乙双方在签署本合同时，对各自的权利、义务、责任清楚明白并愿按合同规定严格执行。如一方违反本合同，另一方有权按合同规定追究违约责任。</p>

<p>本合同一式{{copies}}份，甲乙双方各执{{eachCopies}}份。</p>

<h2>补充条款</h2>

<p>甲方允许乙方隔墙，乙方可以自主装修，乙方可以转租分租。</p>
<p>若甲乙双方任一方违约，需赔偿守约方3个月房租，如是甲方违约另赔偿乙方5万装修款。</p>
<p>免租期为{{freeRentPeriod}}，无需缴纳租金。</p>

<br/>

<table style="width:100%;">
<tr>
<td style="width:50%;">
<p>甲方（签章）：</p>
{{partyASignature}}
<p>电话：{{partyAPhone}}</p>
</td>
<td style="width:50%;">
<p>乙方（签章）：</p>
{{partyBSignature}}
<p>电话：{{partyBPhone}}</p>
</td>
</tr>
</table>

<p style="text-align:right;">签署日期：{{signDate}}</p>
""".strip()

# ---------------------------------------------------------------------------
# 模板变量定义
# ---------------------------------------------------------------------------
LEASE_CONTRACT_VARIABLES = [
    {"name": "partyAName", "label": "甲方（出租方）姓名", "type": "text", "party": "A"},
    {"name": "partyAIdCard", "label": "甲方身份证号码", "type": "text", "party": "A"},
    {"name": "partyAPhone", "label": "甲方电话", "type": "text", "party": "A"},
    {"name": "partyBName", "label": "乙方（承租方）姓名", "type": "text", "party": "B"},
    {"name": "partyBIdCard", "label": "乙方身份证号码", "type": "text", "party": "B"},
    {"name": "partyBPhone", "label": "乙方电话", "type": "text", "party": "B"},
    {"name": "houseAddress", "label": "房屋地址", "type": "text", "party": "common"},
    {"name": "houseArea", "label": "建筑面积（平方米）", "type": "text", "party": "common"},
    {"name": "deliverDate", "label": "交付日期", "type": "date", "party": "common"},
    {"name": "leaseStartDate", "label": "租赁起始日期", "type": "date", "party": "common"},
    {"name": "leaseEndDate", "label": "租赁终止日期", "type": "date", "party": "common"},
    {"name": "renewalNoticeMonths", "label": "续租提前通知月数", "type": "text", "party": "common"},
    {"name": "monthlyRent", "label": "月租金（小写）", "type": "text", "party": "common"},
    {"name": "monthlyRentCapital", "label": "月租金（大写）", "type": "text", "party": "common"},
    {"name": "paymentMethod", "label": "支付方式", "type": "text", "party": "common"},
    {"name": "depositMonths", "label": "保证金月数", "type": "text", "party": "common"},
    {"name": "depositAmount", "label": "保证金金额", "type": "text", "party": "common"},
    {"name": "otherFees", "label": "其他费用项", "type": "text", "party": "common"},
    {"name": "disputeMethod", "label": "争议解决方式编号", "type": "text", "party": "common"},
    {"name": "copies", "label": "合同份数", "type": "text", "party": "common"},
    {"name": "eachCopies", "label": "各执份数", "type": "text", "party": "common"},
    {"name": "freeRentPeriod", "label": "免租期", "type": "text", "party": "common"},
    {"name": "signDate", "label": "签署日期", "type": "date", "party": "common"},
]

# ---------------------------------------------------------------------------
# 签署方配置
# ---------------------------------------------------------------------------
LEASE_CONTRACT_SIGNATORIES = [
    {"role": "甲方（出租方）"},
    {"role": "乙方（承租方）"},
]


# ===========================================================================
# 租房合同（简版 2025-06）
# ===========================================================================
SIMPLE_LEASE_HTML = """
<h1 style="text-align:center;">租 房 合 同</h1>

<p>出租方：{{partyAName}}&emsp;&emsp;手机号：{{partyAPhone}}&emsp;&emsp;（以下简称甲方）</p>
<p>承租方：{{partyBName}}&emsp;&emsp;手机号：{{partyBPhone}}&emsp;&emsp;（以下简称乙方）</p>

<p>根据有关法律、法规规定，在平等、自愿、协商一致的基础上。甲乙双方就下列房屋租赁达成如下协议：</p>

<h3>一、房屋及租期</h3>
<p>甲方将位于 <b>{{communityName}}</b> 小区 <b>{{buildingNo}}</b> 号楼 <b>{{unitNo}}</b> 单元 <b>{{roomNo}}</b> 号房间出租给乙方居住使用，租赁期限为 <b>{{leaseStartDate}}</b> 至 <b>{{leaseEndDate}}</b>，租期为 <b>{{leaseMonths}}</b> 个月，租赁期内，甲方拒租或乙方退租均视为违约。</p>

<h3>二、租金</h3>
<p>本房屋租金为人民币 <b>{{monthlyRent}}</b> 元，租金按 <b>{{paymentCycleMonths}}</b> 个月为一期支付。</p>

<h3>三、付款约定</h3>
<p>乙方需提前7天将房租转给甲方。房租如有拖欠，每天按照月租金的5%支付滞纳金；拖欠达3天及以上甲方可无条件单方面解除合同，并且不退还乙方的押金。</p>

<h3>四、居住人数</h3>
<p>乙方租赁期内，本房屋限住 <b>{{maxOccupants}}</b> 人，如有朋友借住须提供有效合法证件（直系亲属除外），借住时间不得超过3天，超过7天以上，甲方有权单方面解除合约，并且乙方承担朋友居住期间引起的一切后果和损失并承担相应的法律责任，与甲方无关，水电等费用加收双倍，房租另计。</p>

<h3>五、合规义务</h3>
<p>乙方在租赁期间必须主动配合公安、消防、物业以及其他相关部门的检查工作。不能从事违法犯罪活动，应自觉遵守国家法律、法规、政策。租赁期间因违法行为产生的法律责任由乙方自行承担，所产生的损害赔偿责任由乙方自负，甲方不承担任何责任。并且甲方有权单方面解除合约，不退还乙方房租以及押金。</p>

<h3>六、费用承担</h3>
<p>在租赁居住期间：电费 <b>{{electricReading}}</b>、水费 <b>{{waterReading}}</b>、燃气费 <b>{{gasReading}}</b>、网络费 <b>{{networkFee}}</b>、物业费 <b>{{propertyFee}}</b>、卫生费 <b>{{sanitationFee}}</b>、暖气费 <b>{{heatingFee}}</b>（同室友协商，如果不开交30%运行费）以及其他由乙方居住而产生的费用由乙方负担。乙方未按规定结清水、电、燃气等一切费用，甲方有权扣退押金，为了不影响乙方的日常生活，请乙方及时配合物业交纳水电费用，并且备注好自己的房间号。</p>

<h3>七、押金</h3>
<p>乙方同意预交 <b>{{depositAmount}}</b> 元作为押金，钥匙押金 <b>{{keyDeposit}}</b> 元/张，押金在任何时候不能作为房租使用，只有在租赁期满时由甲方结算完相关费用退还给乙方。</p>

<h3>八、甲方违约</h3>
<p>甲方在租赁期内拒租视为违约，除非甲方给乙方安排与原房间条件相当的房间，如不能安排相应的房间则甲方需按日退还乙方的房租，额外补偿乙方一月的租金。</p>

<h3>九、乙方违约</h3>
<p>乙方在租赁期内中途退租视为违规，除非乙方转租他人，但他人需代替乙方履行此合同，乙方违约则乙方所交房租和押金，甲方不予退还，并需额外补偿甲方月租金一倍违约金（租赁期间乙方违约，需转租房子，乙方房租不能逾期，逾期押金不退，需赔偿甲方一个月违约金）。</p>

<h3>十、续租</h3>
<p>租赁期满，甲方有权收回该房屋，乙方如需继续租用的，应提前一个月向甲方提出申请，经甲方同意后，双方重新签订租赁合同，如乙方到期不与甲方联系，本合同将自动延续一年租期。</p>

<h3>十一、房屋维护</h3>
<p>在承租期间，乙方不能改变房屋结构和用途，如需在墙壁上粘贴、美化、装修和订任何东西，需甲方同意，否则按违约责任处理，乙方需要爱护房间配套设施，如有人为损坏，则乙方需照价赔偿，房间电器如空调、洗衣机等因乙方人为使用不当导致损坏，由乙方承担维修费用，耗材如卫生间、走廊灯具损坏由乙方承担；但如有特殊情况可以双方协商调解。甲乙双方签订合同后，乙方验收房间所有物品，如有损坏，请在7个工作日内向甲方保修，维修费用甲方承担，超过7个工作日所维修费用由乙方自行承担。</p>

<h3>十二、甲方有权解除合约的情形</h3>
<p>乙方在居住期间有以下行为的甲方有权单方面解除合约，并不予退还押金：</p>
<ol>
<li>乙方在居住期间应处理好邻里关系，避免大声喧哗，不得影响邻居的生活、休息，如有邻居反映其影响他人正常生活、休息的，超过三次以上甲方有权单方面解除合约；</li>
<li>乙方未经甲方同意，擅自将房间转租或调换使用，甲方可无条件解除双方合同，房租和押金不退，并追究相关损失；</li>
<li>乙方在租赁居住期间生活垃圾应由乙方自行处理，长期未处理，协商无效者，甲方自行请人处理，所出费用将会从乙方住房押金里扣除，如因公共卫生等个人人为问题引起的邻居投诉超过三次者，甲方有权单方面解除合约；</li>
<li>乙方在租赁期内，如私自饲养宠物所造成的一切卫生以及安全隐患，将由乙方承担与甲方无关，如果有人投诉两次以上，甲方有权单方面解除合约，并且不予退还房租及押金。乙方在居住期间，需与其他室友一起打扫公共区域卫生。</li>
</ol>

<h3>十三、退房</h3>
<p>乙方退房时，要把房间所有卫生打扫干净，恢复入住时状况，如若卫生不打扫，保洁清扫费用从乙方住房押金里扣除。</p>

<h3>十四、安全责任</h3>
<p>乙方在租赁居住期间应注意自身人身安全，注意防火防盗，应当安全使用水、电、燃气，禁止超负荷使用电力，如因自身原因（包括自身疾病引起的）产生的人身、财产损坏，乙方自行承担，与甲方无关，并且甲方有权利要求乙方赔偿所造成的一切损失。</p>

<h3>十五、争议解决</h3>
<p>就本合同发生纠纷，双方可协商解决，协商不成，任何一方均可向所在区人民法院提起诉讼，请求司法解决。</p>

<h3>十六、合同份数</h3>
<p>本合同一式两份，甲乙双方各执一份，自双方签字之日起生效，第一期租金需于本合同签订当天付清。</p>

<h3>十七、税费</h3>
<p>本合同租金不含税点，如需发票，乙方承担税点。</p>

<h3>十八、其他</h3>
<p>甲方只认可合同，别的口头承诺，甲方概不认可为合同条款。</p>

<br/>

<table style="width:100%;">
<tr>
<td style="width:50%;">
<p>甲方（签章）：</p>
{{partyASignature}}
<p>身份证号：{{partyAIdCard}}</p>
</td>
<td style="width:50%;">
<p>乙方（签章）：</p>
{{partyBSignature}}
<p>身份证号：{{partyBIdCard}}</p>
</td>
</tr>
</table>

<p style="text-align:right;">合同签订日期：{{signDate}}</p>
""".strip()

SIMPLE_LEASE_VARIABLES = [
    # 甲方信息
    {"name": "partyAName", "label": "出租方姓名", "type": "text", "party": "A"},
    {"name": "partyAPhone", "label": "出租方手机号", "type": "text", "party": "A"},
    {"name": "partyAIdCard", "label": "出租方身份证号", "type": "text", "party": "A"},
    # 乙方信息
    {"name": "partyBName", "label": "承租方姓名", "type": "text", "party": "B"},
    {"name": "partyBPhone", "label": "承租方手机号", "type": "text", "party": "B"},
    {"name": "partyBIdCard", "label": "承租方身份证号", "type": "text", "party": "B"},
    # 房屋信息
    {"name": "communityName", "label": "小区名称", "type": "text", "party": "common"},
    {"name": "buildingNo", "label": "楼号", "type": "text", "party": "common"},
    {"name": "unitNo", "label": "单元号", "type": "text", "party": "common"},
    {"name": "roomNo", "label": "房间号", "type": "text", "party": "common"},
    # 租期
    {"name": "leaseStartDate", "label": "租赁起始日期", "type": "date", "party": "common"},
    {"name": "leaseEndDate", "label": "租赁终止日期", "type": "date", "party": "common"},
    {"name": "leaseMonths", "label": "租期（月）", "type": "text", "party": "common"},
    # 租金
    {"name": "monthlyRent", "label": "月租金（元）", "type": "text", "party": "common"},
    {"name": "paymentCycleMonths", "label": "付款周期（月）", "type": "text", "party": "common"},
    # 居住
    {"name": "maxOccupants", "label": "限住人数", "type": "text", "party": "common"},
    # 费用底数
    {"name": "electricReading", "label": "电表底数", "type": "text", "party": "common"},
    {"name": "waterReading", "label": "水表底数", "type": "text", "party": "common"},
    {"name": "gasReading", "label": "燃气表底数", "type": "text", "party": "common"},
    {"name": "networkFee", "label": "网络费（元/月）", "type": "text", "party": "common"},
    {"name": "propertyFee", "label": "物业费（元/月）", "type": "text", "party": "common"},
    {"name": "sanitationFee", "label": "卫生费（元/月）", "type": "text", "party": "common"},
    {"name": "heatingFee", "label": "暖气费（元/月）", "type": "text", "party": "common"},
    # 押金
    {"name": "depositAmount", "label": "押金金额（元）", "type": "text", "party": "common"},
    {"name": "keyDeposit", "label": "钥匙押金（元/张）", "type": "text", "party": "common"},
    # 签署日期
    {"name": "signDate", "label": "合同签订日期", "type": "date", "party": "common"},
]

SIMPLE_LEASE_SIGNATORIES = [
    {"role": "甲方（出租方）"},
    {"role": "乙方（承租方）"},
]


# ---------------------------------------------------------------------------
# 默认模板列表
# ---------------------------------------------------------------------------
DEFAULT_TEMPLATES = [
    {
        "name": "房屋租赁合同",
        "description": "标准房屋租赁合同模板，适用于个人房屋出租场景",
        "category": "lease",
        "content": LEASE_CONTRACT_HTML,
        "variables": LEASE_CONTRACT_VARIABLES,
        "signatories": LEASE_CONTRACT_SIGNATORIES,
    },
    {
        "name": "租房合同（简版）",
        "description": "简版租房合同，适用于个人房间出租、合租场景，条款简洁实用",
        "category": "lease",
        "content": SIMPLE_LEASE_HTML,
        "variables": SIMPLE_LEASE_VARIABLES,
        "signatories": SIMPLE_LEASE_SIGNATORIES,
    },
]


async def seed_templates():
    """初始化默认合同模板（已存在则更新内容和变量）"""
    try:
        async with async_session_factory() as session:
            for tpl_data in DEFAULT_TEMPLATES:
                result = await session.execute(
                    select(ContractTemplate).where(
                        ContractTemplate.name == tpl_data["name"]
                    )
                )
                existing = result.scalar_one_or_none()
                if existing is None:
                    template = ContractTemplate(**tpl_data)
                    session.add(template)
                    logger.info("合同模板已创建: %s", tpl_data["name"])
                else:
                    # 更新已有模板的内容、变量、签署方配置
                    existing.content = tpl_data["content"]
                    existing.variables = tpl_data["variables"]
                    existing.signatories = tpl_data["signatories"]
                    existing.description = tpl_data["description"]
                    logger.info("合同模板已更新: %s", tpl_data["name"])
            await session.commit()
    except Exception as e:
        logger.warning("初始化合同模板失败: %s", e)
