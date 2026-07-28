# Customer intake

Collect only information needed to plan the trip. Do not request passwords, cookies, full passport numbers, payment-card numbers, verification codes, API keys, or unrelated medical records.

## Blocking minimum

Do not begin broad social research until these are known:

1. destination and travel dates;
2. arrival and departure city, airport, or station;
3. traveler count;
4. actual walking, stairs, terrain, heat, cold, and accessibility limits;
5. booked hotel or intended lodging area for each night;
6. must-do, optional, and do-not-want activities;
7. approximate budget and desired pace;
8. required output language and format.

If exact transport or hotel bookings are not yet available, mark them `UNKNOWN` and produce only a provisional route, not an execution-ready manual.

## Required for an execution-ready manual

Ask for:

- exact flight/train/ferry numbers, dates, times, terminals, and transfer arrangements;
- hotel name, exact address, check-in/out times, and luggage-storage status;
- existing tickets, passes, SIM/eSIM, insurance, and reservations;
- luggage count and approximate size;
- dietary restrictions, allergies, and health limitations that materially affect travel;
- payment cards by network only, mobile-payment availability, and maximum emergency cash;
- willingness to use taxis, start early, return late, or change plans;
- shopping interests and exact products/models when applicable;
- weather thresholds and fallback preferences;
- permission to use official images, maps, or screenshots in the output.

Do not infer reduced mobility from age. Record actual capability in the traveler’s own terms.

## Chinese traveler defaults

Unless the user says otherwise:

- use Simplified Chinese for questions and final delivery;
- ask only for passport jurisdiction and visa/status category needed for research, never a passport number;
- record mainland China departure city and international-transfer constraints;
- record Alipay, WeChat Pay, UnionPay, Visa, and Mastercard availability separately;
- record whether prices should be compared with mainland e-commerce, duty-free, or official retail channels;
- treat emergency cash as a user-defined cap, not the primary payment method;
- ask whether the user can manually log in to Xiaohongshu and other requested platforms in a Chromium browser.

## Platform prerequisites

The customer does not need to understand the tooling. Ask only:

- which supported Chromium browser they use;
- whether they will install/enable the Browser Bridge if needed;
- whether they will manually log in to requested platforms;
- whether read-only access to public posts and comments is allowed;
- which platforms must not be accessed.

Continue with accessible sources when a platform is unavailable and disclose the gap.

## Copyable intake form

```text
目的地和日期：
出发城市、抵达和离境交通：
同行人员：
实际步行、地形和天气耐受：
每晚酒店或住宿区域：
必须安排：
可以安排：
明确不想去：
预算和旅行节奏：
饮食、过敏和必要健康限制：
支付宝/微信/银联/Visa/Mastercard及应急现金上限：
已有机票、门票、电话卡和保险：
行李：
购物兴趣和需要比价的具体产品：
天气、票务或体力变化时的备选偏好：
输出语言和格式：
浏览器及允许只读检索的平台：
已经提供的文件：
```
