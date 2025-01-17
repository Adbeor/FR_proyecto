import numpy as np
from copy import copy

cos = np.cos
sin = np.sin
pi = np.pi


def dh(d, theta, a, alpha):
    cth = np.cos(theta)
    sth = np.sin(theta)
    ca = np.cos(alpha)
    sa = np.sin(alpha)
    T = np.array(
        [
            [cth, -ca * sth, sa * sth, a * cth],
            [sth, ca * cth, -sa * cth, a * sth],
            [0, sa, ca, d],
            [0, 0, 0, 1],
        ]
    )
    return T


def fkine(q):
    """
    Calcular la cinemática directa del robot UR5 dados sus valores articulares.
    q es un vector numpy de la forma [q1, q2, q3, q4, q5, q6]
    """
    # Longitudes (en metros)

    # Matrices DH (completar), emplear la función dh con los parámetros DH para cada articulación
    l1 = 0.02
    l2 = 0.145
    l3 = 0.215
    l4 = 0.16
    l5 = 0.04
    l6 = 0.15

    T1 = dh(l1, q[0], 0, 0)
    T2 = dh(l2, pi / 2, 0, pi / 2 - q[1])
    T3 = dh(l3, pi, 0, q[2])
    T4 = dh(l4, pi / 2, 0, q[3])
    T5 = dh(l5, pi / 2, 0, -q[4])
    T6 = dh(l6, q[5], 0, 0)
    # Efector final con respecto a la base
    T = T1 @ T2 @ T3 @ T4 @ T5 @ T6
    return T


def jacobian_position(q, delta=0.0001):
    """
    Jacobiano analitico para la posicion. Retorna una matriz de 3x6 y toma como
    entrada el vector de configuracion articular q=[q1, q2, q3, q4, q5, q6]

    """
    # Alocacion de memoria
    J = np.zeros((3, 6))
    # Transformacion homogenea inicial (usando q)
    T = fkine(q)

    # Iteracion para la derivada de cada columna
    for i in range(6):
        # Copiar la configuracion articular inicial (usar este dq para cada
        # incremento en una articulacion)
        dq = copy(q)
        # Incrementar la articulacion i-esima usando un delta
        dq[i] = dq[i] + delta
        # Transformacion homogenea luego del incremento (q+delta)
        dT = fkine(dq)
        # Aproximacion del Jacobiano de posicion usando diferencias finitas
        J[:, i] = 1/delta * (dT-T)[0:3, 3]
    return J


def jacobian_pose(q, delta=0.0001):
    """
    Jacobiano analitico para la posicion y orientacion (usando un
    cuaternion). Retorna una matriz de 7x6 y toma como entrada el vector de
    configuracion articular q=[q1, q2, q3, q4, q5, q6]

    """
    J = np.zeros((7, 6))
    # Implementar este Jacobiano aqui

    T = fkine(q)

    for i in range(6):
        dq = copy(q)
        dq[i] = dq[i] + delta
        dT = fkine(dq)
        J[:, i] = 1/delta * (TF2xyzquat(dT)-TF2xyzquat(T)).T
    return J


def rot2quat(R):
    """
    Convertir una matriz de rotacion en un cuaternion

    Entrada:
      R -- Matriz de rotacion
    Salida:
      Q -- Cuaternion [ew, ex, ey, ez]

    """
    dEpsilon = 1e-6
    quat = 4*[0., ]

    quat[0] = 0.5*np.sqrt(R[0, 0]+R[1, 1]+R[2, 2]+1.0)
    if (np.fabs(R[0, 0]-R[1, 1]-R[2, 2]+1.0) < dEpsilon):
        quat[1] = 0.0
    else:
        quat[1] = 0.5*np.sign(R[2, 1]-R[1, 2]) * \
            np.sqrt(R[0, 0]-R[1, 1]-R[2, 2]+1.0)
    if (np.fabs(R[1, 1]-R[2, 2]-R[0, 0]+1.0) < dEpsilon):
        quat[2] = 0.0
    else:
        quat[2] = 0.5*np.sign(R[0, 2]-R[2, 0]) * \
            np.sqrt(R[1, 1]-R[2, 2]-R[0, 0]+1.0)
    if (np.fabs(R[2, 2]-R[0, 0]-R[1, 1]+1.0) < dEpsilon):
        quat[3] = 0.0
    else:
        quat[3] = 0.5*np.sign(R[1, 0]-R[0, 1]) * \
            np.sqrt(R[2, 2]-R[0, 0]-R[1, 1]+1.0)

    return np.array(quat)


def TF2xyzquat(T):
    """
    Convert a homogeneous transformation matrix into the a vector containing the
    pose of the robot.

    Input:
      T -- A homogeneous transformation
    Output:
      X -- A pose vector in the format [x y z ew ex ey ez], donde la first part
           is Cartesian coordinates and the last part is a quaternion
    """
    quat = rot2quat(T[0:3, 0:3])
    res = [T[0, 3], T[1, 3], T[2, 3], quat[0], quat[1], quat[2], quat[3]]
    return np.array(res)


def skew(w):
    R = np.zeros([3, 3])
    R[0, 1] = -w[2]
    R[0, 2] = w[1]
    R[1, 0] = w[2]
    R[1, 2] = -w[0]
    R[2, 0] = -w[1]
    R[2, 1] = w[0]
    return R
