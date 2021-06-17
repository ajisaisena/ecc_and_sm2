from gmssl import sm3, func
from ecc import *
from random import randint
from ecc_math import *
from binascii import a2b_hex


# sm2 数字签名实现
def sm3_hash(message):
    """
    SM3哈希函数调用包装
    :param message: 消息,bytes
    :return: sm3哈希结果,str
    """
    return sm3.sm3_hash(func.bytes_to_list(message))


def hex_format(num):
    """
    十六进制格式化及对齐
    :param num: 需要格式化的数,int
    :return: 格式化结果,str
    """
    result = hex(num)[2:]
    if len(result) % 2 == 1:
        result = '0' + result
    return result


def sm2_sign(z_a, m, pri_a, g, n):
    """
    sm2数字签名
    :param z_a: 杂凑值z_a,str
    :param m: 消息,str
    :param pri_a: 私钥d_a,int
    :param g: 基点G,Point
    :param n: 基点阶数n,int
    :return: 消息及签名，m,[r,s]
    """
    print("z_a: " + z_a + '\n')
    m_byte = m.encode('ascii').hex()
    m_bar = a2b_hex(z_a + m_byte)
    e = int(sm3_hash(m_bar), 16)
    print("e: " + hex(e))
    r = 0
    s = 0
    k = 0x6CB28D99385C175C94F94E934817663FC176D925DD72B727260DBAAE1FB2F96F
    while s == 0:
        k = randint(1, n - 1)
        r_point = g * k
        r = (e + r_point.x) % n
        if r == 0 or r + k == n:
            continue
        s = (get_inv(1 + pri_a, n) * (k - r * pri_a)) % n
    sign = (r, s)
    print("\nr: " + hex(r))
    print("\ns: " + hex(s))
    return m, sign


def sm2_verify(z_a, pub_a, m, r, s, g, n):
    """
    sm2数字签名验证
    :param z_a: 杂凑值z_a, str
    :param pub_a: 公钥p_a, Point
    :param m: 消息m,str
    :param r: 签名r,int
    :param s: 签名s,int
    :param g: 基点G,Point
    :param n: 基点阶数n,int
    :return: sm2数字签名验证结果
    """
    if r < 1 or r > n - 1 or s < 1 or s > n - 1:
        return False
    t = (r + s) % n
    print("t: " + hex(t) + '\n')
    if t == 0:
        return False
    print("z_a: " + z_a + '\n')
    m_byte = m.encode('ascii').hex()
    m_bar = a2b_hex(z_a + m_byte)
    e = int(sm3_hash(m_bar), 16)
    print("e: " + hex(e) + '\n')
    r_point = g * s + pub_a * t
    return (e + r_point.x) % n == r


def zhash_init(identity, g, pub_a):
    """
    杂凑值z_a生成
    :param identity: 用户的身份,str
    :param g: 基点G,Point
    :param pub_a: 公钥p_a,Point
    :return: 杂凑值z_a, str
    """
    entl_a = "{:04X}".format(len(identity) * 8)
    print("entl_a: " + entl_a + '\n')
    id_hex = identity.encode('ascii').hex()
    print("id_hex: " + id_hex + '\n')
    g_x_hex = hex_format(g.x)
    print("g_x_hex: " + g_x_hex + '\n')
    g_y_hex = hex_format(g.y)
    print("g_y_hex: " + g_y_hex + '\n')
    p_a_x_hex = hex_format(pub_a.x)
    print("p_a_x_hex: " + p_a_x_hex + '\n')
    p_a_y_hex = hex_format(pub_a.y)
    print("p_a_y_hex: " + p_a_y_hex + '\n')
    a_hex = hex_format(g.a)
    print("a_hex: " + a_hex + '\n')
    b_hex = hex_format(g.b)
    print("b_hex: " + b_hex + '\n')
    inp = entl_a + id_hex + a_hex + b_hex + g_x_hex + g_y_hex + p_a_x_hex + p_a_y_hex
    print("inp: " + inp + '\n')
    inp = a2b_hex(inp)
    return sm3_hash(inp)


def main():
    m = 'message digest'
    g = Point(0x421DEBD61B62EAB6746434EBC3CC315E32220B3BADD50BDC4C4E6C147FEDD43D,
              0x0680512BCBB42C07D47349D2153B70C4E5D7FDFCBFA36EA1A85841B9E46E09A2,
              0x8542D69E4C044F18E8B92435BF6FF7DE457283915C45517D722EDB8B08F1DFC3,
              0x787968B4FA32C3FD2417842E73BBFEFF2F3C848B6831D7E0EC65228B3937E498,
              0x63E4C6D3B23B0C849CF84241484BFE48F61D59A5B16BA06E6E12D1DA27C5249A)
    p_a = Point(0x0AE4C7798AA0F119471BEE11825BE46202BB79E2A5844495E97C04FF4DF2548A,
                0x7C0240F88F1CD4E16352A73C17B7F16F07353E53A176D684A9FE0C6BB798E857,
                0x8542D69E4C044F18E8B92435BF6FF7DE457283915C45517D722EDB8B08F1DFC3,
                0x787968B4FA32C3FD2417842E73BBFEFF2F3C848B6831D7E0EC65228B3937E498,
                0x63E4C6D3B23B0C849CF84241484BFE48F61D59A5B16BA06E6E12D1DA27C5249A)
    id_a = 'ALICE123@YAHOO.COM'
    d_a = 0x128B2FA8BD433C6C068C8D803DFF79792A519A55171B1B650C23661D15897263
    n = 0x8542D69E4C044F18E8B92435BF6FF7DD297720630485628D5AE74EE7C32E79B7
    m, sign = sm2_sign(zhash_init(id_a, g, p_a), m, d_a, g, n)
    r = sign[0]
    s = sign[1]
    print(sm2_verify(zhash_init(id_a, g, p_a), p_a, m, r, s, g, n))


if __name__ == '__main__':
    main()
